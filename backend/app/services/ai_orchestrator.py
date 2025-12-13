"""AI Model Orchestrator Service

Routes AI tasks to the most appropriate model (Gemini, Claude, etc.)
based on task type, complexity, and cost considerations.
"""

import hashlib
import json
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import google.generativeai as genai

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Import local LLM service (M4 Neural Engine)
try:
    from app.services.local_llm_service import local_llm_service, MLX_AVAILABLE
    LOCAL_LLM_ENABLED = MLX_AVAILABLE and local_llm_service and local_llm_service.is_available()
except ImportError:
    local_llm_service = None
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


class GeminiModel(Enum):
    """Gemini model variants for different complexity levels"""
    FLASH = "gemini-2.0-flash"  # Fast, cheap - complexity 1-4
    PRO = "gemini-2.0-pro"      # Balanced - complexity 5-7
    ULTRA = "gemini-ultra"      # Best quality - complexity 8-10


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
    }

    # Complexity thresholds for model selection
    COMPLEXITY_LOCAL = 4      # 1-4: Use local LLM (M4 Neural Engine) - FREE!
    COMPLEXITY_FLASH = 5      # 5: Use Flash
    COMPLEXITY_PRO = 7        # 6-7: Use Pro
    # 8-10: Use Ultra

    def __init__(self, budget_mode: BudgetMode = BudgetMode.BALANCED):
        self.budget_mode = budget_mode
        self.gemini_models = {
            GeminiModel.FLASH: genai.GenerativeModel('gemini-2.0-flash'),
            GeminiModel.PRO: genai.GenerativeModel('gemini-2.0-pro'),
            # GeminiModel.ULTRA: genai.GenerativeModel('gemini-ultra'),  # Not released yet
        }
        self.local_llm = local_llm_service
        # Claude client would be initialized here when API key is available
        # self.claude_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    
    def route_task(self, task_type: TaskType, complexity: int = None) -> ModelType:
        """
        Determine which model type to use based on task type and complexity.

        Args:
            task_type: Type of AI task
            complexity: 1-10 rating of task complexity (auto-detected if None)

        Returns:
            ModelType to use
        """
        # Auto-detect complexity if not provided
        if complexity is None:
            complexity = self.TASK_COMPLEXITY.get(task_type, 5)

        if complexity <= self.COMPLEXITY_LOCAL:
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

        Args:
            prompt: The generation prompt
            task_type: Type of task for routing
            generation_config: Optional Gemini config
            cache_ttl_hours: Cache TTL in hours

        Returns:
            Generated content as dict
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

        # Get complexity and select model
        complexity = self.TASK_COMPLEXITY.get(task_type, 5)

        # Try local LLM first for simple tasks (complexity 1-4)
        if complexity <= self.COMPLEXITY_LOCAL and LOCAL_LLM_ENABLED:
            try:
                # Use local M4 Neural Engine (FREE and FAST!)
                result = self.local_llm.generate_structured(
                    prompt=prompt,
                    schema={},  # Let LLM infer structure
                    max_tokens=generation_config.get("max_output_tokens", 1024),
                    temperature=generation_config.get("temperature", 0.7),
                )
                _cache_set(cache_key, result, ttl_hours=cache_ttl_hours)
                return result
            except Exception as local_error:
                # Fallback to Gemini if local LLM fails
                print(f"⚠️ Local LLM failed for {task_type.value}, falling back to Gemini: {local_error}")

        # Select Gemini model for complex tasks
        selected_model = self.select_gemini_model(complexity)

        # Try primary model
        try:
            model = self.gemini_models[selected_model]
            response = await model.generate_content_async(prompt, generation_config=generation_config)
            result = json.loads(response.text)
            _cache_set(cache_key, result, ttl_hours=cache_ttl_hours)
            return result
        except Exception as primary_error:
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

        try:
            return await self.generate_with_fallback(
                prompt=prompt,
                task_type=TaskType.CURRICULUM_PLANNING,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 8192,
                    "response_mime_type": "application/json",
                },
                cache_ttl_hours=168  # 1 week
            )
        except Exception:
            # Final fallback to template-based generation
            return self._generate_fallback_curriculum(skill_profile, duration_weeks)
    
    def _build_curriculum_prompt(
        self, 
        skill_profile: Dict[str, Any], 
        duration_weeks: int
    ) -> str:
        """Build the curriculum generation prompt"""
        return f"""You are an expert music education curriculum designer specializing in piano pedagogy.

Create a comprehensive, personalized curriculum for a student with the following profile:

## Student Profile
- Technical Ability: {skill_profile.get('technical_ability', 1)}/10
- Theory Knowledge: {skill_profile.get('theory_knowledge', 1)}/10
- Rhythm Competency: {skill_profile.get('rhythm_competency', 1)}/10
- Ear Training: {skill_profile.get('ear_training', 1)}/10
- Improvisation: {skill_profile.get('improvisation', 1)}/10

## Style Familiarity
{json.dumps(skill_profile.get('style_familiarity', {}), indent=2)}

## Goals
- Primary Goal: {skill_profile.get('primary_goal', 'general improvement')}
- Interests: {', '.join(skill_profile.get('interests', []))}
- Weekly Practice Hours: {skill_profile.get('weekly_practice_hours', 5)}
- Learning Velocity: {skill_profile.get('learning_velocity', 'medium')}

## Curriculum Requirements
- Duration: {duration_weeks} weeks
- Structure: Modules → Lessons → Exercises
- Each module should be 3-6 weeks
- Each lesson should be 1 week
- Each lesson should have 3-7 exercises

Generate a detailed curriculum in the following JSON format:
{{
    "title": "Personalized curriculum title",
    "description": "Brief curriculum overview",
    "modules": [
        {{
            "title": "Module title",
            "description": "Module description",
            "theme": "theme_slug (e.g., gospel_fundamentals)",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["What student will learn"],
            "lessons": [
                {{
                    "title": "Lesson title",
                    "description": "Lesson description",
                    "week_number": 1,
                    "concepts": ["Concept 1", "Concept 2"],
                    "theory_content": {{
                        "summary": "Brief theory explanation",
                        "key_points": ["Point 1", "Point 2"]
                    }},
                    "exercises": [
                        {{
                            "title": "Exercise title",
                            "description": "Exercise description",
                            "exercise_type": "progression|scale|voicing|pattern|rhythm|ear_training",
                            "content": {{
                                "chords": ["Dm7", "G7", "Cmaj7"],
                                "key": "C",
                                "roman_numerals": ["ii7", "V7", "Imaj7"]
                            }},
                            "difficulty": "beginner|intermediate|advanced",
                            "estimated_duration_minutes": 10,
                            "target_bpm": 60
                        }}
                    ]
                }}
            ]
        }}
    ]
}}

Focus on progressive skill building, starting from the student's current level and advancing toward their goals.
Include a variety of exercise types to address all skill areas.
Ensure proper prerequisite ordering in the curriculum.
"""
    
    def _generate_fallback_curriculum(
        self, 
        skill_profile: Dict[str, Any], 
        duration_weeks: int
    ) -> Dict[str, Any]:
        """Generate a template-based curriculum when AI fails"""
        goal = skill_profile.get('primary_goal', 'general')
        
        # Basic template structure
        if 'gospel' in goal.lower():
            modules = [
                {
                    "title": "Gospel Piano Fundamentals",
                    "theme": "gospel_basics",
                    "start_week": 1,
                    "end_week": 4,
                    "outcomes": ["Basic gospel chord shapes", "Common progressions"],
                },
                {
                    "title": "Gospel Voicings & Runs",
                    "theme": "gospel_voicings",
                    "start_week": 5,
                    "end_week": 8,
                    "outcomes": ["Gospel voicing techniques", "Basic runs"],
                },
            ]
        elif 'jazz' in goal.lower():
            modules = [
                {
                    "title": "Jazz Fundamentals",
                    "theme": "jazz_basics",
                    "start_week": 1,
                    "end_week": 4,
                    "outcomes": ["ii-V-I progressions", "Jazz voicings"],
                },
                {
                    "title": "Jazz Improvisation",
                    "theme": "jazz_improv",
                    "start_week": 5,
                    "end_week": 8,
                    "outcomes": ["Scale choices", "Melodic patterns"],
                },
            ]
        else:
            modules = [
                {
                    "title": "Piano Fundamentals",
                    "theme": "fundamentals",
                    "start_week": 1,
                    "end_week": 6,
                    "outcomes": ["Basic technique", "Reading skills"],
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


# Global service instance
ai_orchestrator = AIOrchestrator()
