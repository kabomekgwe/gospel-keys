"""AI Model Orchestrator Service

Routes AI tasks to the most appropriate model (Gemini, Claude, etc.)
based on task type, complexity, and cost considerations.
"""

import hashlib
import json
import logging
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger(__name__)

# Validate GEMINI_API_KEY before configuration
_gemini_api_key = os.environ.get("GEMINI_API_KEY")
if not _gemini_api_key:
    logger.warning(
        "GEMINI_API_KEY not set. AI features will be unavailable. "
        "Set GEMINI_API_KEY environment variable to enable AI curriculum generation."
    )
else:
    try:
        genai.configure(api_key=_gemini_api_key)
        logger.info("✅ Gemini API configured successfully")
    except Exception as e:
        logger.error(f"Failed to configure Gemini API: {e}")
        _gemini_api_key = None

# Import multi-model local LLM service (M4 Neural Engine)
try:
    from app.services.multi_model_service import multi_model_service, MLX_AVAILABLE
    LOCAL_LLM_ENABLED = MLX_AVAILABLE and multi_model_service and multi_model_service.is_available()
except ImportError:
    multi_model_service = None
    LOCAL_LLM_ENABLED = False


class TaskType(Enum):
    """Types of AI tasks for routing"""
    CURRICULUM_PLANNING = "curriculum_planning"
    TUTORIAL_GENERATION = "tutorial_generation"
    CREATIVE_GENERATION = "creative_generation"
    THEORY_ANALYSIS = "theory_analysis"
    STYLE_ANALYSIS = "style_analysis"
    CONTENT_VALIDATION = "content_validation"
    EXERCISE_GENERATION = "exercise_generation"
    PROGRESSION_GENERATION = "progression_generation"
    VOICING_GENERATION = "voicing_generation"
    # Theory-specific task types (Phase 2)
    THEORY_EXPLANATION = "theory_explanation"              # Neo-Riemannian, substitutions, etc.
    THEORY_EXERCISE_GEN = "theory_exercise_generation"     # Generate theory-focused exercises
    SUBSTITUTION_ANALYSIS = "substitution_analysis"        # Analyze chord substitutions
    VOICE_LEADING_ANALYSIS = "voice_leading_analysis"      # Analyze voice leading quality
    # Hybrid music generation (Phase 1)
    HYBRID_MUSIC_GENERATION = "hybrid_music_generation"    # Full music generation pipeline
    CHORD_GENERATION = "chord_generation"                  # musiclang chord generation
    MELODY_GENERATION = "melody_generation"                # Qwen melody generation
    MUSIC_TOKENIZATION = "music_tokenization"              # MidiTok tokenization


class GeminiModel(Enum):
    """Gemini model variants for different complexity levels

    Using production-stable Gemini 1.5 models (not experimental 2.0-exp).
    See: https://ai.google.dev/gemini-api/docs/models
    """
    FLASH = "gemini-1.5-flash"      # Fast, cheap - complexity 1-4
    FLASH_8B = "gemini-1.5-flash-8b"  # Ultra-cheap - complexity 1-2
    PRO = "gemini-1.5-pro"          # Best quality - complexity 5-10


class ModelType(Enum):
    """Available AI models"""
    GEMINI = "gemini"
    CLAUDE = "claude"  # For future integration
    LOCAL = "local"  # Rule-based fallback


class BudgetMode(Enum):
    """Budget optimization modes"""
    COST = "cost"          # Prioritize lowest cost
    BALANCED = "balanced"  # Balance cost and quality
    QUALITY = "quality"    # Prioritize best quality


# Simple in-memory cache (in production, use Redis)
_cache: Dict[str, tuple] = {}  # key -> (value, expiry_time)


def _get_cache_key(task_type: str, prompt: str) -> str:
    """Generate cache key from task type and prompt hash"""
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
    return f"{task_type}:{prompt_hash}"


def _cache_get(key: str) -> Optional[Any]:
    """Get value from cache if not expired"""
    if key in _cache:
        value, expiry = _cache[key]
        if datetime.now() < expiry:
            return value
        del _cache[key]
    return None


def _cache_set(key: str, value: Any, ttl_hours: int = 24) -> None:
    """Set value in cache with TTL"""
    expiry = datetime.now() + timedelta(hours=ttl_hours)
    _cache[key] = (value, expiry)


class AIOrchestrator:
    """
    Orchestrates AI tasks across multiple models.

    Routes tasks to the most appropriate model based on:
    - Task type (curriculum planning → Claude, creative → Gemini)
    - Complexity score (simple → local/cheap, complex → best model)
    - Cost optimization (caching, batching)
    - Fallback chain (if primary fails, try secondary)
    """

    # Model routing configuration
    ROUTING_MAP = {
        TaskType.CURRICULUM_PLANNING: ModelType.GEMINI,  # Use Gemini until Claude is integrated
        TaskType.TUTORIAL_GENERATION: ModelType.GEMINI,
        TaskType.CREATIVE_GENERATION: ModelType.GEMINI,
        TaskType.THEORY_ANALYSIS: ModelType.GEMINI,
        TaskType.STYLE_ANALYSIS: ModelType.GEMINI,
        TaskType.CONTENT_VALIDATION: ModelType.GEMINI,
        TaskType.EXERCISE_GENERATION: ModelType.GEMINI,
        TaskType.PROGRESSION_GENERATION: ModelType.GEMINI,
        TaskType.VOICING_GENERATION: ModelType.GEMINI,
        # Theory-specific tasks (prefer local LLM for cost savings)
        TaskType.THEORY_EXPLANATION: ModelType.LOCAL,
        TaskType.THEORY_EXERCISE_GEN: ModelType.LOCAL,
        TaskType.SUBSTITUTION_ANALYSIS: ModelType.LOCAL,
        TaskType.VOICE_LEADING_ANALYSIS: ModelType.LOCAL,
    }

    # Task complexity scores (1-10 scale)
    TASK_COMPLEXITY = {
        TaskType.CURRICULUM_PLANNING: 8,
        TaskType.TUTORIAL_GENERATION: 7,
        TaskType.EXERCISE_GENERATION: 4,
        TaskType.PROGRESSION_GENERATION: 4,
        TaskType.VOICING_GENERATION: 5,
        TaskType.THEORY_ANALYSIS: 5,
        TaskType.CREATIVE_GENERATION: 6,
        TaskType.STYLE_ANALYSIS: 4,
        TaskType.CONTENT_VALIDATION: 3,
        # Theory-specific task complexities
        TaskType.THEORY_EXPLANATION: 6,           # Qwen2.5-7B (local)
        TaskType.THEORY_EXERCISE_GEN: 4,          # Phi-3.5 Mini (local)
        TaskType.SUBSTITUTION_ANALYSIS: 6,        # Qwen2.5-7B (local)
        TaskType.VOICE_LEADING_ANALYSIS: 5,       # Qwen2.5-7B (local)
    }

    # Complexity thresholds for model selection (3-tier strategy)
    COMPLEXITY_SMALL = 4      # 1-4: Phi-3.5 Mini (local, fast, FREE!)
    COMPLEXITY_MEDIUM = 7     # 5-7: Qwen2.5-7B (local, quality, FREE!)
    # 8-10: Gemini Pro (cloud, complex tasks)

    def __init__(self, budget_mode: BudgetMode = BudgetMode.BALANCED):
        self.budget_mode = budget_mode
        self.gemini_models = {}
        self.initialization_errors = []

        # Only initialize if API key is configured
        if not _gemini_api_key:
            self.initialization_errors.append("GEMINI_API_KEY not configured")
            logger.warning("Skipping Gemini initialization - API key not set")
        else:
            # Initialize Flash model
            try:
                self.gemini_models[GeminiModel.FLASH] = genai.GenerativeModel(
                    GeminiModel.FLASH.value
                )
                logger.info(f"✅ Initialized Gemini model: {GeminiModel.FLASH.value}")
            except Exception as e:
                error_msg = f"Failed to initialize {GeminiModel.FLASH.value}: {e}"
                self.initialization_errors.append(error_msg)
                logger.error(error_msg, exc_info=True)

            # Initialize Pro model
            try:
                self.gemini_models[GeminiModel.PRO] = genai.GenerativeModel(
                    GeminiModel.PRO.value
                )
                logger.info(f"✅ Initialized Gemini model: {GeminiModel.PRO.value}")
            except Exception as e:
                error_msg = f"Failed to initialize {GeminiModel.PRO.value}: {e}"
                self.initialization_errors.append(error_msg)
                logger.error(error_msg, exc_info=True)

        self.multi_llm = multi_model_service
        # Claude client would be initialized here when API key is available
        # self.claude_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    def is_available(self) -> bool:
        """Check if AI orchestrator has any working models"""
        if LOCAL_LLM_ENABLED:
            return True  # Local LLM can handle requests
        return len(self.gemini_models) > 0

    def get_status(self) -> Dict[str, Any]:
        """Get detailed status of AI models for diagnostics"""
        status = {
            "gemini_available": len(self.gemini_models) > 0,
            "gemini_models_loaded": [m.value for m in self.gemini_models.keys()],
            "local_llm_available": LOCAL_LLM_ENABLED,
            "initialization_errors": self.initialization_errors,
            "budget_mode": self.budget_mode.value,
        }

        # Add multi-model service info if available
        if LOCAL_LLM_ENABLED and self.multi_llm:
            status["multi_model_info"] = self.multi_llm.get_model_info()

        return status

    def route_task(self, task_type: TaskType, complexity: int = None) -> ModelType:
        """
        Determine which model type to use based on task type and complexity.

        3-Tier Routing Strategy:
        - Complexity 1-4: Phi-3.5 Mini (local, fast)
        - Complexity 5-7: Qwen2.5-7B (local, quality)
        - Complexity 8-10: Gemini Pro (cloud, complex)

        Args:
            task_type: Type of AI task
            complexity: 1-10 rating of task complexity (auto-detected if None)

        Returns:
            ModelType to use
        """
        # Check for forced local LLM
        if settings.force_local_llm and LOCAL_LLM_ENABLED:
            return ModelType.LOCAL

        # Auto-detect complexity if not provided
        if complexity is None:
            complexity = self.TASK_COMPLEXITY.get(task_type, 5)

        # Use local models for complexity 1-7 (90% of tasks!)
        if complexity <= self.COMPLEXITY_MEDIUM and LOCAL_LLM_ENABLED:
            return ModelType.LOCAL

        return self.ROUTING_MAP.get(task_type, ModelType.GEMINI)

    def select_gemini_model(self, complexity: int) -> GeminiModel:
        """
        Select the appropriate Gemini model based on complexity and budget mode.

        Args:
            complexity: 1-10 rating of task complexity

        Returns:
            GeminiModel to use
        """
        # Budget mode adjustments
        if self.budget_mode == BudgetMode.COST:
            # Always use Flash for cost optimization
            return GeminiModel.FLASH
        elif self.budget_mode == BudgetMode.QUALITY:
            # Use Pro for medium+, Ultra for high complexity
            if complexity >= 8:
                return GeminiModel.ULTRA if GeminiModel.ULTRA in self.gemini_models else GeminiModel.PRO
            elif complexity >= 5:
                return GeminiModel.PRO
            else:
                return GeminiModel.FLASH
        else:  # BALANCED
            # Standard complexity-based routing
            if complexity >= 8:
                return GeminiModel.PRO  # Would be ULTRA when available
            elif complexity >= self.COMPLEXITY_FLASH:
                return GeminiModel.PRO if complexity >= self.COMPLEXITY_PRO else GeminiModel.FLASH
            else:
                return GeminiModel.FLASH
    
    async def generate_with_fallback(
        self,
        prompt: str,
        task_type: TaskType,
        generation_config: Dict[str, Any] = None,
        cache_ttl_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Generate AI content with automatic fallback chain.

        Fallback order: Local LLM (M4) → Pro/Ultra → Flash → Error
        """
        # Check cache
        cache_key = _get_cache_key(task_type.value, prompt)
        cached = _cache_get(cache_key)
        if cached:
            return cached

        # Default generation config
        if generation_config is None:
            generation_config = {
                "temperature": 0.7,
                "max_output_tokens": 4096,
                "response_mime_type": "application/json",
            }

        # Get complexity
        complexity = self.TASK_COMPLEXITY.get(task_type, 5)

        # Check if we should use local LLM (either logical preference or forced)
        # NEW: Multi-model strategy now handles complexity 1-7 (90% of tasks!)
        use_local = LOCAL_LLM_ENABLED and (
            complexity <= self.COMPLEXITY_MEDIUM or settings.force_local_llm
        )

        # Try local multi-model LLM first (Phi-3.5 or Llama 3.3 70B)
        if use_local:
            try:
                # Use local M4 Neural Engine (FREE and FAST!)
                # Automatically selects Phi-3.5 (1-4) or Llama 3.3 70B (5-10) based on complexity
                logger.info(f"🤖 Using local multi-model LLM for {task_type.value} (complexity {complexity})")
                result = self.multi_llm.generate_structured(
                    prompt=prompt,
                    schema={},  # Let LLM infer structure
                    complexity=complexity,  # Pass complexity for model selection
                    max_tokens=generation_config.get("max_output_tokens", 1024),
                    temperature=generation_config.get("temperature", 0.7),
                    force_local=settings.force_local_llm,  # Allow 8-10 complexity on local
                )
                logger.info(f"✅ Local LLM succeeded for {task_type.value}")
                _cache_set(cache_key, result, ttl_hours=cache_ttl_hours)
                return result
            except Exception as local_error:
                # Fallback to Gemini if local LLM fails
                logger.warning(f"⚠️ Local LLM failed for {task_type.value}, falling back to Gemini: {local_error}")
        
        # Select Gemini model for complex tasks (or fallback)

        # Select Gemini model for complex tasks
        selected_model = self.select_gemini_model(complexity)

        # Try primary model
        try:
            # Validate models are available
            if not self.gemini_models:
                raise ValueError(
                    "No Gemini models available. Check GEMINI_API_KEY configuration."
                )

            # Fallback to Flash if selected model not available
            if selected_model not in self.gemini_models:
                logger.warning(
                    f"Selected model {selected_model.value} not available, "
                    f"falling back to {GeminiModel.FLASH.value}"
                )
                if GeminiModel.FLASH in self.gemini_models:
                    selected_model = GeminiModel.FLASH
                else:
                    raise ValueError("No fallback model available")

            model = self.gemini_models[selected_model]
            response = await model.generate_content_async(prompt, generation_config=generation_config)

            # Parse response
            try:
                result = json.loads(response.text)
            except json.JSONDecodeError as json_err:
                logger.error(
                    f"Failed to parse Gemini response as JSON: {json_err}",
                    extra={"response_text": response.text[:500]}  # Log first 500 chars
                )
                raise

            _cache_set(cache_key, result, ttl_hours=cache_ttl_hours)
            return result
        except Exception as primary_error:
            error_details = {
                "task_type": task_type.value,
                "selected_model": selected_model.value if selected_model in self.gemini_models else "none",
                "error_type": type(primary_error).__name__,
                "error_message": str(primary_error)
            }
            logger.error("Gemini API call failed", extra=error_details)
            # Fallback to Flash if we were using Pro/Ultra
            if selected_model != GeminiModel.FLASH:
                try:
                    flash_model = self.gemini_models[GeminiModel.FLASH]
                    response = await flash_model.generate_content_async(prompt, generation_config=generation_config)
                    result = json.loads(response.text)
                    _cache_set(cache_key, result, ttl_hours=cache_ttl_hours)
                    return result
                except Exception:
                    pass  # Fall through to template generation

            # All AI models failed - return error
            raise Exception(f"All AI models failed for {task_type.value}: {str(primary_error)}")

    async def generate_curriculum_plan(
        self,
        skill_profile: Dict[str, Any],
        duration_weeks: int = 12
    ) -> Dict[str, Any]:
        """
        Generate a complete curriculum plan based on user's skill profile.

        Uses AI to create a personalized learning path with fallback.
        """
        prompt = self._build_curriculum_prompt(skill_profile, duration_weeks)
        
        # Determine which model will be used
        complexity = self.TASK_COMPLEXITY.get(TaskType.CURRICULUM_PLANNING, 8)
        expected_model = self.route_task(TaskType.CURRICULUM_PLANNING, complexity)
        logger.info(
            f"🎓 Generating curriculum: complexity={complexity}, "
            f"expected_model={expected_model.value}, "
            f"duration={duration_weeks} weeks, "
            f"goal={skill_profile.get('primary_goal', 'unknown')}"
        )

        try:
            result = await self.generate_with_fallback(
                prompt=prompt,
                task_type=TaskType.CURRICULUM_PLANNING,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 8192,
                    "response_mime_type": "application/json",
                },
                cache_ttl_hours=168  # 1 week
            )
            
            # Validate curriculum quality
            is_valid, issues = self._validate_curriculum_quality(result)
            if is_valid:
                logger.info(f"✅ Curriculum generated successfully with {len(result.get('modules', []))} modules")
                return result
            else:
                logger.warning(f"⚠️ Curriculum quality issues detected: {issues}")
                logger.info("🔄 Using fallback template due to incomplete AI response")
                return self._generate_fallback_curriculum(skill_profile, duration_weeks)
            
        except Exception as e:
            logger.error(f"❌ Curriculum generation failed: {e}")
            # Final fallback to template-based generation
            return self._generate_fallback_curriculum(skill_profile, duration_weeks)
    
    def _validate_curriculum_quality(self, curriculum: Dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate that generated curriculum meets quality standards."""
        issues = []
        
        modules = curriculum.get('modules', [])
        if not modules:
            issues.append("No modules generated")
            return False, issues
        
        for i, module in enumerate(modules):
            lessons = module.get('lessons', [])
            if not lessons:
                issues.append(f"Module {i+1} has no lessons")
                continue
            
            for j, lesson in enumerate(lessons):
                exercises = lesson.get('exercises', [])
                if not exercises:
                    issues.append(f"Module {i+1}, Lesson {j+1} has no exercises")
                elif len(exercises) < 2:
                    issues.append(f"Module {i+1}, Lesson {j+1} has only {len(exercises)} exercise(s)")
                
                # Check for theory content
                if not lesson.get('theory_content'):
                    issues.append(f"Module {i+1}, Lesson {j+1} missing theory_content")
        
        return len(issues) == 0, issues
    
    def _build_curriculum_prompt(
        self, 
        skill_profile: Dict[str, Any], 
        duration_weeks: int
    ) -> str:
        """Build the curriculum generation prompt with world-class quality requirements"""
        
        # Determine primary style focus from interests
        interests = skill_profile.get('interests', ['general'])
        primary_style = interests[0] if interests else 'general'
        
        return f"""You are a WORLD-CLASS music education curriculum designer with 20+ years of experience teaching piano.
Your curriculums are known for being comprehensive, engaging, and producing real results.

Create a PREMIUM, DETAILED curriculum for a student with this profile:

## Student Profile
- Technical Ability: {skill_profile.get('technical_ability', 1)}/10
- Theory Knowledge: {skill_profile.get('theory_knowledge', 1)}/10
- Rhythm Competency: {skill_profile.get('rhythm_competency', 1)}/10
- Ear Training: {skill_profile.get('ear_training', 1)}/10
- Improvisation: {skill_profile.get('improvisation', 1)}/10

## Style Familiarity
{json.dumps(skill_profile.get('style_familiarity', {}), indent=2)}

## Goals & Preferences
- Primary Goal: {skill_profile.get('primary_goal', 'general improvement')}
- Musical Interests: {', '.join(interests)}
- Weekly Practice Hours: {skill_profile.get('weekly_practice_hours', 5)}
- Learning Velocity: {skill_profile.get('learning_velocity', 'medium')}

## ⚠️ CRITICAL QUALITY REQUIREMENTS ⚠️

Your curriculum MUST be RICH and DETAILED. Generic or sparse content is UNACCEPTABLE.

### Module Requirements:
- Create {max(2, duration_weeks // 4)} modules covering {duration_weeks} weeks
- Each module MUST have 2-4 detailed lessons
- Each module MUST have clear, specific learning outcomes (not generic statements)

### Lesson Requirements:
- Each lesson MUST have 3-5 HIGH-QUALITY exercises
- Each lesson MUST have theory_content with:
  - "summary": 2-3 sentence explanation of the concept
  - "key_points": Array of 3-5 practical, specific takeaways
- Each lesson MUST list specific "concepts" being taught

### Exercise Requirements (MOST IMPORTANT):
Each exercise MUST have COMPLETE, DETAILED content:

1. **For progression exercises** - Include:
   - "chords": Full chord symbols with extensions (e.g., "Dm9", "G13", "Cmaj9#11")
   - "roman_numerals": Proper analysis (e.g., "ii9", "V13", "Imaj9")
   - "key": The musical key
   - "voicing_suggestions": How to voice these chords
   - "tips": Array of 2-3 practice tips

2. **For voicing exercises** - Include:
   - "chord": The target chord (e.g., "Cmaj9")
   - "notes": Specific notes in the voicing (e.g., ["C", "E", "G", "B", "D"])
   - "register": "low", "mid", or "high"
   - "voice_leading_from": What chord it connects from

3. **For scale exercises** - Include:
   - "scale": Scale name (e.g., "Mixolydian", "Gospel Scale", "Blues Scale")
   - "key": Starting note
   - "pattern": Practice pattern description
   - "application": How to use it musically

4. **For rhythm exercises** - Include:
   - "time_signature": e.g., "4/4", "6/8"
   - "pattern": Rhythmic pattern description
   - "groove_style": e.g., "swing", "straight", "gospel shuffle"

### Example of HIGH-QUALITY Exercise (FOLLOW THIS FORMAT):
{{
    "title": "The Gospel 7-3-6 Turnaround",
    "description": "Master the classic gospel turnaround used in countless hymns and worship songs. This progression creates beautiful tension and resolution through secondary dominants.",
    "exercise_type": "progression",
    "content": {{
        "chords": ["Gdim7", "C7(b9)", "Fm9", "Fm9/Bb"],
        "roman_numerals": ["vii°7/vi", "V7/vi", "vi9", "vi9/IV"],
        "key": "Ab",
        "voicing_suggestions": "Use close voicings with the diminished chord, spread for the minor 9th",
        "tips": [
            "Practice the voice leading between Gdim7 and C7 first",
            "Let the b9 on C7 resolve down to the root of Fm",
            "Start at 60 BPM and gradually increase to 90 BPM"
        ]
    }},
    "difficulty": "intermediate",
    "estimated_duration_minutes": 15,
    "target_bpm": 70
}}

## Output Format (JSON):
{{
    "title": "Creative, engaging curriculum title reflecting the {primary_style} focus",
    "description": "Compelling 2-3 sentence overview that excites the student about their journey",
    "modules": [
        {{
            "title": "Module title (specific, not generic)",
            "description": "What this module covers and why it matters",
            "theme": "{primary_style}_specific_theme",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["Specific skill 1", "Specific skill 2", "Specific skill 3"],
            "lessons": [
                {{
                    "title": "Lesson title",
                    "description": "Compelling lesson description",
                    "week_number": 1,
                    "concepts": ["Concept 1", "Concept 2", "Concept 3"],
                    "theory_content": {{
                        "summary": "Clear, educational 2-3 sentence explanation",
                        "key_points": ["Point 1", "Point 2", "Point 3"]
                    }},
                    "estimated_duration_minutes": 45,
                    "exercises": [
                        // 3-5 DETAILED exercises following the format above
                    ]
                }}
            ]
        }}
    ]
}}

## Final Instructions:
1. Make this curriculum SO GOOD that students will want to share it with friends
2. Include style-specific techniques and vocabulary for {primary_style}
3. Build progressively - each lesson should build on the previous
4. Balance theory, technique, and creative application
5. Include real songs or standards when appropriate for context
6. Return ONLY valid JSON - no markdown, no explanations outside the JSON
"""
    
    def _generate_fallback_curriculum(
        self,
        skill_profile: Dict[str, Any],
        duration_weeks: int
    ) -> Dict[str, Any]:
        """Generate a template-based curriculum when AI fails - WITH FULL LESSONS"""
        goal = skill_profile.get('primary_goal', 'general_musicianship') or 'general_musicianship'

        # Comprehensive fallback with full lessons and exercises
        if 'gospel' in goal.lower():
            modules = [
                {
                    "title": "Gospel Piano Fundamentals",
                    "description": "Build your foundation in gospel piano with essential chord shapes and progressions.",
                    "theme": "gospel_basics",
                    "start_week": 1,
                    "end_week": 6,
                    "outcomes": ["Basic gospel chord shapes", "Common progressions", "Proper hand positioning"],
                    "lessons": [
                        {
                            "title": "Essential Gospel Chords",
                            "description": "Learn the core major 7th, minor 7th, and dominant 7th chords used in gospel music.",
                            "week_number": 1,
                            "concepts": ["Major 7th chords", "Minor 7th chords", "Dominant 7th chords"],
                            "theory_content": {
                                "summary": "Gospel music relies heavily on extended chords. We start with 7th chords as the foundation.",
                                "key_points": ["Major 7 = bright, jazzy sound", "Dominant 7 = tension that resolves", "Minor 7 = soulful, mellow"]
                            },
                            "exercises": [
                                {
                                    "title": "Major 7th Chord Practice",
                                    "description": "Play Cmaj7, Fmaj7, Gmaj7 in root position.",
                                    "exercise_type": "voicing",
                                    "content": {
                                        "chords": ["Cmaj7", "Fmaj7", "Gmaj7"],
                                        "key": "C",
                                        "tips": ["Keep fingers curved", "Use proper fingering: 1-2-3-5"]
                                    },
                                    "difficulty": "beginner",
                                    "estimated_duration_minutes": 10
                                },
                                {
                                    "title": "Gospel 1-4-5 Progression",
                                    "description": "The most common gospel progression in the key of C.",
                                    "exercise_type": "progression",
                                    "content": {
                                        "chords": ["Cmaj7", "Fmaj7", "G7", "Cmaj7"],
                                        "roman_numerals": ["Imaj7", "IVmaj7", "V7", "Imaj7"],
                                        "key": "C",
                                        "tips": ["Let each chord ring", "Practice with a metronome at 70 BPM"]
                                    },
                                    "difficulty": "beginner",
                                    "estimated_duration_minutes": 15
                                }
                            ]
                        },
                        {
                            "title": "Gospel Turnarounds",
                            "description": "Master the classic 1-6-2-5 turnaround used in countless gospel songs.",
                            "week_number": 2,
                            "concepts": ["Turnarounds", "Circle of fifths movement", "Voice leading"],
                            "theory_content": {
                                "summary": "Turnarounds create harmonic motion that leads back to the beginning. The 1-6-2-5 is essential.",
                                "key_points": ["Creates forward momentum", "Each chord leads naturally to the next", "Used at the end of phrases"]
                            },
                            "exercises": [
                                {
                                    "title": "Classic Gospel Turnaround",
                                    "description": "1-6-2-5 in the key of C.",
                                    "exercise_type": "progression",
                                    "content": {
                                        "chords": ["Cmaj7", "Am7", "Dm7", "G7"],
                                        "roman_numerals": ["Imaj7", "vi7", "ii7", "V7"],
                                        "key": "C",
                                        "tips": ["Focus on smooth voice leading", "Keep the common tones between chords"]
                                    },
                                    "difficulty": "beginner",
                                    "estimated_duration_minutes": 15
                                }
                            ]
                        }
                    ]
                },
            ]
        elif 'jazz' in goal.lower():
            modules = [
                {
                    "title": "Jazz Piano Fundamentals",
                    "description": "Build your jazz vocabulary with essential voicings and the most important progression in jazz.",
                    "theme": "jazz_basics",
                    "start_week": 1,
                    "end_week": 6,
                    "outcomes": ["ii-V-I progressions", "Jazz voicings", "Shell voicings"],
                    "lessons": [
                        {
                            "title": "The ii-V-I Progression",
                            "description": "Master the most important chord progression in jazz music.",
                            "week_number": 1,
                            "concepts": ["ii-V-I", "Chord functions", "Resolution"],
                            "theory_content": {
                                "summary": "The ii-V-I is the backbone of jazz harmony. Understanding it unlocks thousands of jazz standards.",
                                "key_points": ["ii chord creates motion", "V chord builds tension", "I chord resolves"]
                            },
                            "exercises": [
                                {
                                    "title": "Basic ii-V-I in C",
                                    "description": "Play Dm7-G7-Cmaj7 with root position voicings.",
                                    "exercise_type": "progression",
                                    "content": {
                                        "chords": ["Dm7", "G7", "Cmaj7"],
                                        "roman_numerals": ["ii7", "V7", "Imaj7"],
                                        "key": "C",
                                        "tips": ["Listen for the resolution", "Practice in all 12 keys eventually"]
                                    },
                                    "difficulty": "beginner",
                                    "estimated_duration_minutes": 15
                                },
                                {
                                    "title": "Shell Voicings",
                                    "description": "Learn 3-note voicings with root, 3rd, and 7th.",
                                    "exercise_type": "voicing",
                                    "content": {
                                        "chord": "Dm7",
                                        "notes": ["D", "F", "C"],
                                        "voicing_type": "shell"
                                    },
                                    "difficulty": "beginner",
                                    "estimated_duration_minutes": 10
                                }
                            ]
                        }
                    ]
                },
            ]
        else:
            modules = [
                {
                    "title": "Piano Fundamentals",
                    "description": "Build a solid foundation with proper technique and basic music reading skills.",
                    "theme": "fundamentals",
                    "start_week": 1,
                    "end_week": 6,
                    "outcomes": ["Basic technique", "Reading skills", "Hand independence"],
                    "lessons": [
                        {
                            "title": "Hand Position & Basic Technique",
                            "description": "Learn proper hand positioning and finger technique at the piano.",
                            "week_number": 1,
                            "concepts": ["Hand position", "Finger curvature", "Relaxed wrists"],
                            "theory_content": {
                                "summary": "Good technique starts with proper hand position. This prevents injury and enables faster progress.",
                                "key_points": ["Keep fingers curved", "Wrists relaxed and level", "Sit at proper height"]
                            },
                            "exercises": [
                                {
                                    "title": "C Major Scale",
                                    "description": "Practice the C major scale with proper fingering.",
                                    "exercise_type": "scale",
                                    "content": {
                                        "scale": "C Major",
                                        "key": "C",
                                        "fingering": "1-2-3-1-2-3-4-5"
                                    },
                                    "difficulty": "beginner",
                                    "estimated_duration_minutes": 10
                                },
                                {
                                    "title": "Simple Chord Practice",
                                    "description": "Play C, F, and G major triads.",
                                    "exercise_type": "voicing",
                                    "content": {
                                        "chords": ["C", "F", "G"],
                                        "key": "C"
                                    },
                                    "difficulty": "beginner",
                                    "estimated_duration_minutes": 10
                                }
                            ]
                        }
                    ]
                },
            ]
        
        return {
            "title": f"Personalized {goal.title()} Curriculum",
            "description": f"A {duration_weeks}-week curriculum tailored to your goals.",
            "modules": modules,
        }
    
    async def generate_exercise_content(
        self,
        exercise_type: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate content for a specific exercise type"""
        cache_key = _get_cache_key(f"exercise_{exercise_type}", json.dumps(context, sort_keys=True))
        cached = _cache_get(cache_key)
        if cached:
            return cached
        
        prompt = self._build_exercise_prompt(exercise_type, context)
        
        try:
            response = await self.gemini_model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.8,
                    "max_output_tokens": 2048,
                    "response_mime_type": "application/json",
                }
            )
            
            result = json.loads(response.text)
            _cache_set(cache_key, result, ttl_hours=72)
            return result
            
        except Exception:
            return self._generate_fallback_exercise(exercise_type, context)
    
    def _build_exercise_prompt(self, exercise_type: str, context: Dict[str, Any]) -> str:
        """Build prompt for exercise generation"""
        key = context.get('key', 'C')
        difficulty = context.get('difficulty', 'beginner')
        style = context.get('style', 'general')
        
        if exercise_type == "progression":
            return f"""Generate a chord progression exercise in {key} major for a {difficulty} level student.
Style: {style}

Return JSON:
{{
    "chords": ["chord1", "chord2", ...],
    "roman_numerals": ["I", "IV", ...],
    "key": "{key}",
    "suggestions": ["practice tip 1", "tip 2"],
    "voicing_hints": ["hint 1", "hint 2"]
}}
"""
        elif exercise_type == "scale":
            return f"""Generate a scale exercise in {key} for a {difficulty} level student.

Return JSON:
{{
    "scale": "major/minor/mode name",
    "key": "{key}",
    "octaves": 1 or 2,
    "practice_patterns": ["ascending", "descending", ...],
    "tempo_range": [slow_bpm, fast_bpm]
}}
"""
        else:
            return f"""Generate a {exercise_type} exercise in {key} for a {difficulty} level student.

Return JSON with appropriate content for this exercise type.
"""
    
    def _generate_fallback_exercise(
        self, 
        exercise_type: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate fallback exercise content"""
        key = context.get('key', 'C')
        
        if exercise_type == "progression":
            return {
                "chords": ["Cmaj7", "Fmaj7", "Dm7", "G7"],
                "roman_numerals": ["Imaj7", "IVmaj7", "ii7", "V7"],
                "key": key,
            }
        elif exercise_type == "scale":
            return {
                "scale": "major",
                "key": key,
                "octaves": 1,
            }
        else:
            return {"key": key}
    
    async def analyze_theory(self, content: str) -> Dict[str, Any]:
        """Analyze musical content for theory concepts"""
        prompt = f"""Analyze the following musical content and identify theory concepts:

{content}

Return JSON:
{{
    "key_center": "detected key",
    "chord_functions": ["function analysis"],
    "notable_techniques": ["technique 1", "technique 2"],
    "difficulty_rating": 1-10,
    "teaching_points": ["point 1", "point 2"]
}}
"""

        try:
            response = await self.gemini_model.generate_content_async(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 1024,
                    "response_mime_type": "application/json",
                }
            )
            return json.loads(response.text)
        except Exception:
            return {"error": "Analysis failed"}

    async def generate_personalized_curriculum_with_history(
        self,
        skill_profile: Dict[str, Any],
        performance_history: Optional[Dict[str, Any]] = None,
        duration_weeks: int = 12
    ) -> Dict[str, Any]:
        """
        Generate curriculum with performance-aware personalization.

        This enhanced version includes user's past performance to create
        a more adaptive curriculum that addresses specific struggles.

        Args:
            skill_profile: User's skill levels and preferences
            performance_history: Past performance data (optional)
            duration_weeks: Curriculum duration

        Returns:
            Enhanced curriculum with performance-aware adaptations
        """
        # Build enhanced prompt with performance context
        base_prompt = self._build_curriculum_prompt(skill_profile, duration_weeks)

        if performance_history:
            perf_context = self._build_performance_context(performance_history)
            enhanced_prompt = f"{base_prompt}\n\n{perf_context}"
        else:
            enhanced_prompt = base_prompt

        try:
            return await self.generate_with_fallback(
                prompt=enhanced_prompt,
                task_type=TaskType.CURRICULUM_PLANNING,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 8192,
                    "response_mime_type": "application/json",
                },
                cache_ttl_hours=24  # Shorter cache for personalized content
            )
        except Exception:
            return self._generate_fallback_curriculum(skill_profile, duration_weeks)

    def _build_performance_context(self, performance_history: Dict[str, Any]) -> str:
        """Build performance context for enhanced prompts"""
        weak_areas = performance_history.get('weak_skill_areas', [])
        strong_areas = performance_history.get('strong_skill_areas', [])
        avg_quality = performance_history.get('avg_quality_score', 0)
        trend = performance_history.get('recent_performance_trend', 'stable')
        consecutive_struggles = performance_history.get('consecutive_struggles', 0)

        context = """## Performance History Context

**Recent Performance:**
"""

        if avg_quality > 0:
            quality_assessment = "excellent" if avg_quality > 4.0 else "good" if avg_quality > 3.0 else "struggling"
            context += f"- Average quality score: {avg_quality:.1f}/5.0 ({quality_assessment})\n"

        context += f"- Performance trend: {trend}\n"

        if consecutive_struggles > 0:
            context += f"- Consecutive difficulties: {consecutive_struggles} recent exercises\n"

        if weak_areas:
            context += f"\n**Areas Needing Attention:**\n"
            for area in weak_areas:
                context += f"- {area}: Requires additional practice and simpler exercises\n"

        if strong_areas:
            context += f"\n**Strong Areas:**\n"
            for area in strong_areas:
                context += f"- {area}: Can introduce advanced concepts here\n"

        context += """
**Adaptation Instructions:**
1. For weak areas: Start with fundamentals, increase repetition, provide more guidance
2. For strong areas: Accelerate pace, introduce complex variations
3. Balance challenge to maintain motivation
4. If performance is declining: reduce difficulty and increase support
5. If performance is improving: gradually increase complexity

Create a curriculum that directly addresses these performance patterns.
"""

        return context

    async def generate_contextual_tutorial(
        self,
        lesson_content: Dict[str, Any],
        user_skill_level: Dict[str, float],
        user_struggles: Optional[List[str]] = None
    ) -> str:
        """
        Generate tutorial that references user's actual skill level and struggles.

        Args:
            lesson_content: Lesson details (title, concepts, etc.)
            user_skill_level: User's skill scores
            user_struggles: Areas where user is struggling

        Returns:
            Personalized tutorial text
        """
        prompt = f"""You are a patient, expert piano teacher creating a personalized lesson tutorial.

## Lesson Content
- Title: {lesson_content.get('title')}
- Concepts: {', '.join(lesson_content.get('concepts', []))}
- Description: {lesson_content.get('description')}

## Student's Current Level
- Technical Ability: {user_skill_level.get('technical_ability', 5)}/10
- Theory Knowledge: {user_skill_level.get('theory_knowledge', 5)}/10
- Rhythm: {user_skill_level.get('rhythm_competency', 5)}/10
"""

        if user_struggles:
            prompt += f"\n## Known Struggles\nThis student has been struggling with:\n"
            for struggle in user_struggles:
                prompt += f"- {struggle}\n"
            prompt += "\nAddress these struggles directly in your explanation. Break down difficult concepts into simpler steps.\n"

        prompt += """
## Tutorial Guidelines
1. Start with a friendly introduction that acknowledges their current level
2. Explain concepts clearly, using analogies when helpful
3. Break complex ideas into digestible steps
4. Provide specific practice tips related to their struggles
5. End with encouragement and next steps
6. Keep tone conversational and supportive
7. Reference their strengths to build confidence

Write a comprehensive tutorial (400-600 words) that feels personally crafted for this student.
"""

        try:
            response = await self.generate_with_fallback(
                prompt=prompt,
                task_type=TaskType.TUTORIAL_GENERATION,
                generation_config={
                    "temperature": 0.8,
                    "max_output_tokens": 2048,
                    "response_mime_type": "text/plain",
                },
                cache_ttl_hours=1  # Short cache for personalized content
            )
            return response if isinstance(response, str) else response.get('text', 'Tutorial generation failed')
        except Exception as e:
            return f"Welcome to this lesson on {lesson_content.get('title')}! Let's dive into these concepts together."

    async def generate_exercise_feedback(
        self,
        exercise_title: str,
        quality_score: float,
        exercise_type: str,
        user_skill_level: float
    ) -> str:
        """
        Generate contextual feedback based on exercise performance.

        Args:
            exercise_title: Exercise name
            quality_score: 0-5 performance score
            exercise_type: Type of exercise
            user_skill_level: User's skill in this area (0-10)

        Returns:
            Personalized feedback message
        """
        if quality_score >= 4.0:
            tone = "congratulatory"
            focus = "next challenge"
        elif quality_score >= 3.0:
            tone = "encouraging"
            focus = "refinement tips"
        else:
            tone = "supportive"
            focus = "simplification and fundamentals"

        prompt = f"""Generate brief, {tone} feedback for a piano student.

**Exercise:** {exercise_title}
**Type:** {exercise_type}
**Performance Score:** {quality_score}/5.0
**Student's Skill Level:** {user_skill_level}/10

Provide 2-3 sentences that:
1. Acknowledge their performance
2. Give {focus}
3. Maintain positive, growth-oriented tone

Be specific to the exercise type and performance level."""

        try:
            response = await self.generate_with_fallback(
                prompt=prompt,
                task_type=TaskType.CONTENT_VALIDATION,
                generation_config={
                    "temperature": 0.9,
                    "max_output_tokens": 256,
                    "response_mime_type": "text/plain",
                },
                cache_ttl_hours=0  # No cache for dynamic feedback
            )
            return response if isinstance(response, str) else response.get('text', 'Great work!')
        except Exception:
            if quality_score >= 4.0:
                return f"Excellent work on {exercise_title}! You're showing real mastery here."
            elif quality_score >= 3.0:
                return f"Nice progress on {exercise_title}! Focus on consistency and you'll have this down soon."
            else:
                return f"Keep practicing {exercise_title}. Try slowing down the tempo to build accuracy first."


# Global service instance
ai_orchestrator = AIOrchestrator()
