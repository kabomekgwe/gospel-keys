"""Assessment Schemas for API Request/Response"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# === Assessment Content Models ===

class AssessmentExercise(BaseModel):
    """A practical exercise in an assessment"""
    id: str
    type: str  # scales, progression, voicing, etc.
    instruction: str
    evaluation_criteria: List[str]
    points: int


class AssessmentQuestion(BaseModel):
    """A theory/knowledge question"""
    id: str
    question: str
    type: str  # multiple_choice, true_false, short_answer
    options: Optional[List[str]] = None
    correct_answer: Optional[int | str] = None
    points: int


class AssessmentSection(BaseModel):
    """A section of the assessment"""
    section_id: str
    title: str
    weight: float
    exercises: Optional[List[AssessmentExercise]] = None
    questions: Optional[List[AssessmentQuestion]] = None


class AssessmentContent(BaseModel):
    """Full assessment structure"""
    title: str
    duration_minutes: int
    sections: List[AssessmentSection]


# === Request Models ===

class AssessmentResponse(BaseModel):
    """User's response to an assessment"""
    assessment_id: str
    responses: Dict[str, any] = Field(
        ...,
        description="Question/exercise ID → response mapping"
    )


# === Response Models ===

class AssessmentInfo(BaseModel):
    """Basic assessment information"""
    id: str
    user_id: int
    curriculum_id: Optional[str]
    assessment_type: str
    created_at: datetime
    overall_score: Optional[float] = None


class AssessmentEvaluation(BaseModel):
    """Assessment evaluation results"""
    assessment_id: str
    scores: Dict[str, float] = Field(
        ...,
        description="Skill area → score mapping (1-10 scale)"
    )
    overall_score: float
    feedback: Dict[str, any] = Field(
        ...,
        description="Detailed feedback with strengths, improvements, focus areas"
    )


class SkillProfileUpdate(BaseModel):
    """Updated skill profile after assessment"""
    user_id: int
    technical_ability: int
    theory_knowledge: int
    rhythm_competency: int
    ear_training: int
    improvisation: int
    updated_at: datetime
