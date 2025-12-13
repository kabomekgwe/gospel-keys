"""Assessment Generation and Evaluation Service

Generates AI-powered assessments for skill evaluation and provides
intelligent scoring with personalized feedback.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.curriculum_models import Curriculum, Assessment
from app.database.models import User, UserSkillProfile
from app.services.ai_orchestrator import ai_orchestrator, TaskType

logger = logging.getLogger(__name__)


class AssessmentType(str, Enum):
    """Types of assessments"""
    DIAGNOSTIC = "diagnostic"      # Initial skill evaluation
    MILESTONE = "milestone"        # Progress check (week 4, 8)
    MODULE = "module"              # End of module
    FINAL = "final"                # End of curriculum


class AssessmentService:
    """Service for generating and evaluating assessments"""

    def __init__(self, db: AsyncSession):
        self.db = db

        # Assessment section weights
        self.SECTION_WEIGHTS = {
            "technical": 0.3,
            "theory": 0.2,
            "ear_training": 0.15,
            "rhythm": 0.15,
            "improvisation": 0.2
        }

    async def generate_diagnostic_assessment(
        self,
        user_id: int
    ) -> Assessment:
        """Generate initial diagnostic assessment for a user

        Args:
            user_id: User ID

        Returns:
            Assessment model instance
        """
        try:
            # Get or create skill profile
            result = await self.db.execute(
                select(UserSkillProfile).where(UserSkillProfile.user_id == user_id)
            )
            profile = result.scalar_one_or_none()

            if not profile:
                # Create default profile
                profile = UserSkillProfile(
                    user_id=user_id,
                    technical_ability=1,
                    theory_knowledge=1,
                    rhythm_competency=1,
                    ear_training=1,
                    improvisation=1
                )
                self.db.add(profile)
                await self.db.commit()

            # Build assessment prompt
            prompt = self._build_diagnostic_prompt(profile)

            # Generate assessment content via AI
            assessment_content = await ai_orchestrator.generate_with_fallback(
                prompt=prompt,
                task_type=TaskType.EXERCISE_GENERATION,  # Reuse exercise generation
                generation_config={
                    "temperature": 0.8,
                    "max_output_tokens": 3072,
                },
                cache_ttl_hours=168  # 7 days
            )

            # Create assessment record
            assessment = Assessment(
                user_id=user_id,
                curriculum_id=None,
                assessment_type=AssessmentType.DIAGNOSTIC,
                scores_json=json.dumps({}),
                ai_feedback_json=json.dumps(assessment_content),
                recommendations_json=json.dumps([])
            )
            self.db.add(assessment)
            await self.db.commit()
            await self.db.refresh(assessment)

            logger.info(f"Generated diagnostic assessment for user {user_id}")

            return assessment

        except Exception as e:
            logger.error(f"Failed to generate diagnostic assessment: {e}")
            raise e

    async def generate_milestone_assessment(
        self,
        curriculum: Curriculum,
        week: int
    ) -> Assessment:
        """Generate milestone assessment for curriculum progress

        Args:
            curriculum: Curriculum model instance
            week: Current week number

        Returns:
            Assessment model instance
        """
        try:
            # Build assessment prompt
            prompt = self._build_milestone_prompt(curriculum, week)

            # Generate assessment content
            assessment_content = await ai_orchestrator.generate_with_fallback(
                prompt=prompt,
                task_type=TaskType.EXERCISE_GENERATION,
                generation_config={
                    "temperature": 0.8,
                    "max_output_tokens": 2048,
                },
                cache_ttl_hours=72
            )

            # Create assessment record
            assessment = Assessment(
                user_id=curriculum.user_id,
                curriculum_id=curriculum.id,
                assessment_type=AssessmentType.MILESTONE,
                scores_json=json.dumps({}),
                ai_feedback_json=json.dumps(assessment_content),
                recommendations_json=json.dumps([])
            )
            self.db.add(assessment)
            await self.db.commit()
            await self.db.refresh(assessment)

            logger.info(f"Generated milestone assessment for curriculum {curriculum.id}, week {week}")

            return assessment

        except Exception as e:
            logger.error(f"Failed to generate milestone assessment: {e}")
            raise e

    async def evaluate_assessment(
        self,
        assessment_id: str,
        responses: Dict
    ) -> Dict:
        """Evaluate user responses to an assessment using AI

        Args:
            assessment_id: Assessment ID
            responses: User responses dict

        Returns:
            Evaluation results with scores and feedback
        """
        try:
            # Get assessment
            result = await self.db.execute(
                select(Assessment).where(Assessment.id == assessment_id)
            )
            assessment = result.scalar_one_or_none()

            if not assessment:
                raise ValueError(f"Assessment not found: {assessment_id}")

            # Build evaluation prompt
            assessment_content = json.loads(assessment.ai_feedback_json)
            prompt = self._build_evaluation_prompt(assessment_content, responses)

            # Evaluate via AI
            evaluation = await ai_orchestrator.generate_with_fallback(
                prompt=prompt,
                task_type=TaskType.THEORY_ANALYSIS,
                generation_config={
                    "temperature": 0.3,  # More deterministic for scoring
                    "max_output_tokens": 2048,
                }
            )

            # Extract scores
            scores = evaluation.get("scores", {})
            overall_score = evaluation.get("overall_score", 0)
            feedback = evaluation.get("feedback", {})

            # Update assessment
            assessment.scores_json = json.dumps(scores)
            assessment.overall_score = overall_score
            assessment.recommendations_json = json.dumps(
                feedback.get("recommended_focus", [])
            )

            await self.db.commit()

            logger.info(f"Evaluated assessment {assessment_id}: overall score {overall_score}")

            return {
                "assessment_id": assessment_id,
                "scores": scores,
                "overall_score": overall_score,
                "feedback": feedback
            }

        except Exception as e:
            logger.error(f"Failed to evaluate assessment {assessment_id}: {e}")
            raise e

    async def update_skill_profile_from_assessment(
        self,
        user_id: int,
        scores: Dict[str, float]
    ) -> UserSkillProfile:
        """Update user's skill profile based on assessment scores

        Args:
            user_id: User ID
            scores: Skill area scores (1-10 scale)

        Returns:
            Updated UserSkillProfile
        """
        try:
            # Get skill profile
            result = await self.db.execute(
                select(UserSkillProfile).where(UserSkillProfile.user_id == user_id)
            )
            profile = result.scalar_one_or_none()

            if not profile:
                raise ValueError(f"Skill profile not found for user {user_id}")

            # Update scores (weighted average with existing scores)
            # New score gets 60% weight, existing gets 40%
            if "technical_ability" in scores:
                profile.technical_ability = int(
                    profile.technical_ability * 0.4 + scores["technical_ability"] * 0.6
                )

            if "theory_knowledge" in scores:
                profile.theory_knowledge = int(
                    profile.theory_knowledge * 0.4 + scores["theory_knowledge"] * 0.6
                )

            if "rhythm_competency" in scores:
                profile.rhythm_competency = int(
                    profile.rhythm_competency * 0.4 + scores["rhythm_competency"] * 0.6
                )

            if "ear_training" in scores:
                profile.ear_training = int(
                    profile.ear_training * 0.4 + scores["ear_training"] * 0.6
                )

            if "improvisation" in scores:
                profile.improvisation = int(
                    profile.improvisation * 0.4 + scores["improvisation"] * 0.6
                )

            profile.updated_at = datetime.utcnow()

            await self.db.commit()
            await self.db.refresh(profile)

            logger.info(f"Updated skill profile for user {user_id}")

            return profile

        except Exception as e:
            logger.error(f"Failed to update skill profile for user {user_id}: {e}")
            raise e

    def _build_diagnostic_prompt(self, profile: UserSkillProfile) -> str:
        """Build AI prompt for diagnostic assessment generation"""
        prompt = f"""Generate a comprehensive diagnostic piano assessment in JSON format.

Current Skill Profile:
- Technical Ability: {profile.technical_ability}/10
- Theory Knowledge: {profile.theory_knowledge}/10
- Rhythm Competency: {profile.rhythm_competency}/10
- Ear Training: {profile.ear_training}/10
- Improvisation: {profile.improvisation}/10

Generate an assessment with the following JSON structure:

{{
  "title": "Gospel Piano Diagnostic Assessment",
  "duration_minutes": 20,
  "sections": [
    {{
      "section_id": "technical",
      "title": "Technical Ability",
      "weight": 0.3,
      "exercises": [
        {{
          "id": "tech_1",
          "type": "scales",
          "instruction": "Play C major scale, 2 octaves",
          "evaluation_criteria": ["accuracy", "tempo", "evenness"],
          "points": 10
        }}
      ]
    }},
    {{
      "section_id": "theory",
      "title": "Theory Knowledge",
      "weight": 0.2,
      "questions": [
        {{
          "id": "theory_1",
          "question": "What notes are in a Cmaj7 chord?",
          "type": "multiple_choice",
          "options": ["C-E-G-B", "C-E-G-Bb", "C-Eb-G-B", "C-E-G-A"],
          "correct_answer": 0,
          "points": 5
        }}
      ]
    }},
    {{
      "section_id": "ear_training",
      "title": "Ear Training",
      "weight": 0.15,
      "exercises": [...]
    }},
    {{
      "section_id": "rhythm",
      "title": "Rhythm",
      "weight": 0.15,
      "exercises": [...]
    }},
    {{
      "section_id": "improvisation",
      "title": "Improvisation",
      "weight": 0.2,
      "exercises": [...]
    }}
  ]
}}

Focus on Gospel piano style. Include 3-5 items per section.
Ensure total assessment takes about 20 minutes.
"""
        return prompt

    def _build_milestone_prompt(self, curriculum: Curriculum, week: int) -> str:
        """Build AI prompt for milestone assessment generation"""
        prompt = f"""Generate a milestone assessment for week {week} of a {curriculum.duration_weeks}-week curriculum.

Curriculum: {curriculum.title}
Current Week: {week}

Generate a focused assessment (10-15 minutes) testing progress on concepts covered in weeks 1-{week}.

Use the same JSON structure as diagnostic assessment, but with fewer items (2-3 per section).
Focus on practical application of learned concepts.
"""
        return prompt

    def _build_evaluation_prompt(self, assessment_content: Dict, responses: Dict) -> str:
        """Build AI prompt for response evaluation"""
        prompt = f"""Evaluate this piano assessment performance and provide scores.

Assessment: {json.dumps(assessment_content, indent=2)}

Student Responses: {json.dumps(responses, indent=2)}

Return JSON:
{{
  "scores": {{
    "technical_ability": 7,
    "theory_knowledge": 6,
    "ear_training": 5,
    "rhythm_competency": 8,
    "improvisation": 6
  }},
  "overall_score": 6.5,
  "feedback": {{
    "strengths": ["Good chord recognition", "Solid rhythm"],
    "areas_for_improvement": ["Voicing technique", "Improvisation"],
    "recommended_focus": ["gospel_fundamentals", "ear_training"]
  }},
  "suggested_difficulty": "intermediate"
}}

Scores are on a 1-10 scale. Provide constructive, specific feedback.
"""
        return prompt


# Note: This service requires a database session, so no singleton instance
