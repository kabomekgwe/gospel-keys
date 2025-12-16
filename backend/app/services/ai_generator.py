"""AI Music Theory Generator Service using Google Gemini with Claude fallback"""

import json
import os
import re
import subprocess
import base64
from pathlib import Path
from typing import Optional

import google.generativeai as genai
from anthropic import Anthropic
try:
    from mlx_lm import load, generate
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False

from app.schemas.ai import (
    ProgressionRequest, ProgressionResponse, ChordInfo,
    ReharmonizationRequest, ReharmonizationResponse,
    VoicingRequest, VoicingResponse, VoicingInfo,
    VoiceLeadingRequest, VoiceLeadingResponse,
    ExerciseRequest, ExerciseResponse, ExerciseStep,
    SubstitutionRequest, SubstitutionResponse,
    LicksRequest, LicksResponse, LickInfo,
    LickStyle, ContextType, Difficulty,
    GeneratorInfo, GeneratorsListResponse, GeneratorCategory,
    ArrangeRequest, ArrangeResponse,
    SplitVoicingRequest, SplitVoicingResponse,
    # New enhanced types
    CreativityLevel, EducationalContent, CreativeVariation,
    VoiceLeadingAnalysis, PhrasePosition, Emotion,
)
from app.core.config import settings
from app.jazz.lick_patterns import lick_pattern_service

# Import genre DNA and style reference services
from app.services.genre_dna import (
    get_genre_prompt_context,
    get_creativity_instruction,
    get_genre_avoid_list,
    get_genre_reference_artists,
)
from app.services.style_reference import (
    get_style_reference_prompt,
    get_artist_style,
)

# Import genre arrangers
from app.gospel.arrangement.arranger import GospelArranger
from app.jazz.arrangement.arranger import JazzArranger
from app.neosoul.arrangement.arranger import NeosoulArranger
from app.blues.arrangement.arranger import BluesArranger
from app.classical.arrangement.arranger import ClassicalArranger
from app.gospel.midi.enhanced_exporter import export_enhanced_midi

from app.services.template_loader import template_loader



# Configure Gemini
if settings.google_api_key:
    genai.configure(api_key=settings.google_api_key)


# Note to MIDI mapping
NOTE_TO_MIDI = {
    'C': 60, 'C#': 61, 'Db': 61, 'D': 62, 'D#': 63, 'Eb': 63,
    'E': 64, 'F': 65, 'F#': 66, 'Gb': 66, 'G': 67, 'G#': 68,
    'Ab': 68, 'A': 69, 'A#': 70, 'Bb': 70, 'B': 71
}


def note_to_midi(note: str, octave: int = 4) -> int:
    """Convert note name to MIDI number"""
    # Parse note name and octave
    match = re.match(r'^([A-G][#b]?)(\d)?$', note)
    if match:
        note_name = match.group(1)
        oct = int(match.group(2)) if match.group(2) else octave
        base = NOTE_TO_MIDI.get(note_name, 60)
        return base + (oct - 4) * 12
    return 60  # Default to middle C


def parse_json_from_response(text: str) -> dict:
    """Extract JSON from Gemini response text"""
    # Try to find JSON block
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
    if json_match:
        return json.loads(json_match.group(1))

    # Try direct JSON parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON object
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            return json.loads(json_match.group(0))

    raise ValueError(f"Could not parse JSON from response: {text[:200]}")


def check_claude_cli_available() -> bool:
    """Check if Claude CLI is available in the system"""
    try:
        result = subprocess.run(
            ["which", "claude"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


class AIGeneratorService:
    """Service for AI-powered music theory generation using Gemini with Claude fallback"""

    def __init__(self):
        # Initialize Gemini (primary)
        self.gemini_available = False
        if settings.google_api_key:
            try:
                genai.configure(api_key=settings.google_api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                self.gemini_available = True
            except Exception as e:
                print(f"Warning: Gemini initialization failed: {e}")

        # Initialize Claude API (fallback option 1)
        self.claude_api_available = False
        if settings.anthropic_api_key:
            try:
                self.claude = Anthropic(api_key=settings.anthropic_api_key)
                self.claude_api_available = True
            except Exception as e:
                print(f"Warning: Claude API initialization failed: {e}")

        # Check for Claude CLI (fallback option 2 - uses your existing subscription)
        self.claude_cli_available = check_claude_cli_available()
        if self.claude_cli_available:
            print("✅ Claude CLI detected - will use your existing Claude Code subscription")

        # Initialize MLX (Local Mac GPU)
        self.mlx_available = MLX_AVAILABLE
        self.mlx_model = None
        self.mlx_tokenizer = None
        self.mlx_model_path = "mlx-community/Qwen2.5-14B-Instruct-4bit"

        # Ensure at least one AI provider is available
        if not self.gemini_available and not self.claude_api_available and not self.claude_cli_available and not self.mlx_available:
            raise ValueError("No AI provider available. Please set GOOGLE_API_KEY, ANTHROPIC_API_KEY, install 'mlx-lm', or ensure 'claude' CLI is installed")
    
    def get_available_generators(self) -> GeneratorsListResponse:
        """Get list of all available generators by category"""
        generators = {
            "progressions": [
                GeneratorInfo(
                    id="progression",
                    name="Chord Progression Generator",
                    description="Generate chord progressions in various styles (jazz, gospel, pop, etc.)",
                    category=GeneratorCategory.PROGRESSIONS
                ),
                GeneratorInfo(
                    id="reharmonization",
                    name="Reharmonization Engine",
                    description="Get reharmonization suggestions for existing progressions",
                    category=GeneratorCategory.PROGRESSIONS
                ),
            ],
            "voicings": [
                GeneratorInfo(
                    id="voicing",
                    name="Chord Voicing Generator",
                    description="Generate multiple voicing options for any chord",
                    category=GeneratorCategory.VOICINGS
                ),
                GeneratorInfo(
                    id="voice_leading",
                    name="Voice Leading Optimizer",
                    description="Find optimal voice leading between two chords",
                    category=GeneratorCategory.VOICINGS
                ),
            ],
            "exercises": [
                GeneratorInfo(
                    id="exercise",
                    name="Practice Exercise Generator",
                    description="Create custom exercises for scales, arpeggios, and more",
                    category=GeneratorCategory.EXERCISES
                ),
            ],
            "analysis": [
                GeneratorInfo(
                    id="substitution",
                    name="Chord Substitution Finder",
                    description="Get substitution options for any chord",
                    category=GeneratorCategory.ANALYSIS
                ),
            ],
        }
        return GeneratorsListResponse(generators=generators)
    

    async def generate_progression(self, request: ProgressionRequest, template_id: Optional[str] = None) -> ProgressionResponse:
        """Generate a chord progression using Gemini with enhanced context.
        
        Enhanced with:
        - Genre-specific DNA for authentic style generation
        - Artist style references for targeted creativity
        - Creativity level instructions
        - Optional educational content
        - Optional variation generation
        - Optional template context for curriculum-driven generation
        """
        # Build prompt
        prompt_parts = []
        
        # 1. Template Context (Highest Priority)
        engine_data = None
        if template_id:
            # Try to load template data
            found_data = template_loader.find_exercise_by_id(template_id)
            if found_data:
                # Extract engine_data if available
                engine_data = found_data.get("engine_data") or found_data.get("musical_data")
                
                # Build context prompt
                context = f"""
TARGET CURRICULUM EXERCISE: {found_data.get('name') or found_data.get('title')}
INSTRUCTIONS: {found_data.get('instructions') or found_data.get('pedagogy', {}).get('objective')}
THEORY FOCUS: {found_data.get('theory_prompt') or found_data.get('pedagogy', {}).get('theory_summary')}

SPECIFIC PARAMETERS (engine_data):
{json.dumps(engine_data, indent=2) if engine_data else "None"}

Generate the progression adhering strictly to these instructional constraints.
"""
                prompt_parts.append(context)


        # Build enhanced prompt with genre DNA
        genre_context = get_genre_prompt_context(request.style.value)
        creativity_instruction = get_creativity_instruction(request.creativity.value)
        
        # Add artist style reference if provided
        style_reference_prompt = ""
        if request.style_reference:
            style_reference_prompt = get_style_reference_prompt(request.style_reference)
        
        prompt_parts.append(f"You are an expert music producer and composer specializing in {request.style.value} music.")
        prompt_parts.append(f"Generate a {request.length}-chord progression in the key of {request.key} {request.mode}.")
        prompt_parts.append(genre_context)
        prompt_parts.append(creativity_instruction)
        prompt_parts.append(style_reference_prompt)
        
        prompt_parts.append(f"""
Additional Parameters:
- Mood: {request.mood.value if request.mood else 'Not specified'}
- Extensions: {'Include rich extensions (7ths, 9ths, 11ths, 13ths)' if request.include_extensions else 'Use basic triads'}

Return a JSON object with this exact structure:
{{
    "progression": [
        {{
            "symbol": "Cmaj9",
            "notes": ["C", "E", "G", "B", "D"],
            "midi_notes": [48, 52, 55, 59, 62],
            "function": "Imaj9",
            "comment": "Rich tonic with added 9th for color"
        }}
    ],
    "analysis": "Detailed analysis explaining the harmonic choices and why they work for this style",
    "tips": ["Performance tip 1", "Voicing suggestion", "Interpretation advice"],
    "education": {{
        "why_it_works": "Theory explanation of what makes this progression effective",
        "alternatives": ["Alternative chord that could work at position 2", "Another option"],
        "theory_concepts": ["Concept 1 used", "Concept 2 used"]
    }}
}}

CRITICAL REQUIREMENTS:
1. Make it sound AUTHENTICALLY {request.style.value} - avoid generic progressions
2. Each chord must have correct notes and MIDI numbers
3. MIDI notes in playable piano range (C3-C6, MIDI 48-84)
4. Include insightful roman numeral analysis
5. Provide genuinely helpful tips, not generic advice
6. Return ONLY the JSON, no other text""")

        prompt = "\n\n".join(prompt_parts)

        data = await self._generate_with_fallback(prompt, "progression")
        
        # Build educational content if requested
        education = None
        if request.include_education and "education" in data:
            edu_data = data["education"]
            education = EducationalContent(
                why_it_works=edu_data.get("why_it_works", ""),
                alternatives=edu_data.get("alternatives", []),
                theory_concepts=edu_data.get("theory_concepts", []),
                listen_to=[artist["name"] for artist in get_genre_reference_artists(request.style.value)[:3]]
            )
        
        # Generate variations if requested
        variations = None
        variations_data = None
        if request.generate_variations:
            variations, variations_data = await self._generate_progression_variations(request, data)

        return ProgressionResponse(
            progression=[ChordInfo(**chord) for chord in data["progression"]],
            key=request.key,
            style=request.style.value,
            analysis=data.get("analysis"),
            tips=data.get("tips"),
            education=education,
            variations=variations,
            variations_data=variations_data,
            engine_data=engine_data,
        )
    
    async def _generate_progression_variations(
        self, 
        request: ProgressionRequest, 
        original_data: dict
    ) -> tuple[list[CreativeVariation], list[list[ChordInfo]]]:
        """Generate alternative progression variations."""
        variations = []
        variations_data = []
        
        # Conservative variation
        conservative_prompt = f"""Generate a more CONSERVATIVE version of this {request.style.value} progression.
Stay within established patterns. Make it sound like a textbook example.
Key: {request.key} {request.mode}, Length: {request.length} chords.
Return JSON with "progression" array only."""
        
        try:
            conservative_data = await self._generate_with_fallback(conservative_prompt, "progression_conservative")
            variations.append(CreativeVariation(
                label="Safe Bet",
                creativity_score=0.3,
                description="Classic, proven progression that stays within the idiom"
            ))
            variations_data.append([ChordInfo(**c) for c in conservative_data.get("progression", [])])
        except Exception:
            pass  # Skip if generation fails
        
        # Adventurous variation
        adventurous_prompt = f"""Generate a BOLD, SURPRISING version of a {request.style.value} progression.
Push boundaries with unexpected but beautiful harmonic choices.
Key: {request.key} {request.mode}, Length: {request.length} chords.
Return JSON with "progression" array only."""
        
        try:
            adventurous_data = await self._generate_with_fallback(adventurous_prompt, "progression_adventurous")
            variations.append(CreativeVariation(
                label="Bold Move",
                creativity_score=0.8,
                description="Adventurous progression with unexpected harmonic turns"
            ))
            variations_data.append([ChordInfo(**c) for c in adventurous_data.get("progression", [])])
        except Exception:
            pass
        
        return variations, variations_data
    
    async def generate_reharmonization(self, request: ReharmonizationRequest) -> ReharmonizationResponse:
        """Generate reharmonization suggestions using hybrid local+AI approach

        Strategy:
        1. Use local Phase 6 orchestrator for rule-based reharmonization
        2. For simple tasks (complexity ≤ 7): Return local results
        3. For complex tasks (complexity 8+): Enhance with AI explanations
        4. Apply boldness level to filter/rank reharmonization options
        """
        from app.pipeline.reharmonization_orchestrator import get_all_reharmonizations_for_chord
        from app.theory.chord_parser import parse_chord_symbol

        # Parse original progression
        parsed_chords = []
        for chord_symbol in request.original_progression:
            try:
                parsed = parse_chord_symbol(chord_symbol)
                parsed_chords.append(parsed)
            except Exception:
                # If parsing fails, use fallback format
                parsed_chords.append({'root': chord_symbol, 'quality': ''})

        # Determine complexity based on request characteristics
        complexity = self._calculate_reharmonization_complexity(request)
        
        # Map creativity level to boldness factor
        boldness_map = {
            CreativityLevel.CONSERVATIVE: 0.3,  # Prefer safe, traditional options
            CreativityLevel.BALANCED: 0.5,      # Mix of safe and bold
            CreativityLevel.ADVENTUROUS: 0.7,   # Prefer creative options
            CreativityLevel.EXPERIMENTAL: 0.9,  # Maximum boldness
        }
        boldness = boldness_map.get(request.creativity, 0.5)
        
        # Adjust min_score based on boldness (lower = allow bolder options)
        min_score = max(0.4, 0.8 - boldness * 0.4)  # Range: 0.4 to 0.8

        # Get local rule-based reharmonization options
        reharmonized_chords = []
        techniques_used = set()

        for i, chord_dict in enumerate(parsed_chords):
            # Get context (previous/next chords)
            previous = None
            if i > 0:
                prev_chord = parsed_chords[i-1]
                previous = (prev_chord.get('root', ''), prev_chord.get('quality', ''))

            next_chord = None
            if i < len(parsed_chords) - 1:
                next_c = parsed_chords[i+1]
                next_chord = (next_c.get('root', ''), next_c.get('quality', ''))

            # Get reharmonization options from Phase 6 orchestrator
            options = get_all_reharmonizations_for_chord(
                chord_dict=chord_dict,
                key=request.key,
                previous_chord=previous,
                next_chord=next_chord,
                genre=request.style.value.lower(),
                max_options=5,  # Get more options for boldness filtering
                min_score=min_score
            )

            # Select option based on boldness
            if options:
                # Higher boldness = prefer lower-ranking (more adventurous) options
                option_index = min(int(len(options) * boldness), len(options) - 1)
                best = options[option_index]
                techniques_used.add(best['technique'])

                # Convert to ChordInfo format
                chord_info = self._convert_to_chord_info(
                    root=best['new_root'],
                    quality=best['new_quality'],
                    original=chord_dict
                )
                reharmonized_chords.append(chord_info)
            else:
                # No good options, keep original
                chord_info = self._convert_to_chord_info(
                    root=chord_dict.get('root', ''),
                    quality=chord_dict.get('quality', ''),
                    original=chord_dict
                )
                reharmonized_chords.append(chord_info)

        # Generate explanation
        if complexity <= 7:
            # Simple case: Use local rule-based explanation
            explanation = self._generate_local_explanation(
                techniques=list(techniques_used),
                style=request.style.value
            )
            source = "local_rules"
        else:
            # Complex case: Enhance with AI explanation
            original = " - ".join(request.original_progression)
            reharmonized_symbols = [c.symbol for c in reharmonized_chords]
            reharmonized = " - ".join(reharmonized_symbols)

            prompt = f"""Explain this reharmonization in {request.style.value} style:

Original: {original}
Reharmonized: {reharmonized}
Techniques used: {', '.join(techniques_used)}
Key: {request.key}
Boldness: {request.creativity.value if request.creativity else 'balanced'}

Provide a clear, educational explanation (2-3 sentences) of why these reharmonization choices work well for this style."""

            explanation = await self._generate_with_fallback(prompt, "reharmonization_explanation")
            if isinstance(explanation, dict):
                explanation = explanation.get('explanation', str(explanation))
            source = "hybrid"
        
        # Generate educational content if requested
        education = None
        if request.include_education:
            education = EducationalContent(
                why_it_works=f"This reharmonization uses {', '.join(list(techniques_used)[:3])} to transform the original progression while maintaining harmonic function.",
                alternatives=[
                    f"Try tritone substitution on the V chord for more tension",
                    f"Add passing diminished chords between steps",
                    f"Use modal interchange to borrow from parallel minor/major",
                ],
                theory_concepts=list(techniques_used)[:5],
            )
        
        # Generate variations if requested
        variations = None
        variations_data = None
        if request.generate_variations:
            variations, variations_data = await self._generate_reharmonization_variations(
                request, reharmonized_chords
            )

        return ReharmonizationResponse(
            original=request.original_progression,
            reharmonized=reharmonized_chords,
            explanation=explanation,
            techniques_used=list(techniques_used),
            source=source,  # Track whether local or hybrid was used
            complexity=complexity,
            education=education,
            variations=variations,
            variations_data=variations_data,
        )

    def _calculate_reharmonization_complexity(self, request: ReharmonizationRequest) -> int:
        """Calculate task complexity (1-10) for reharmonization request"""
        complexity = 5  # Base complexity

        # More chords = higher complexity
        num_chords = len(request.original_progression)
        if num_chords <= 4:
            complexity += 0
        elif num_chords <= 8:
            complexity += 1
        else:
            complexity += 2

        # Style impacts complexity
        style_complexity = {
            'jazz': 1,
            'gospel': 1,
            'neosoul': 2,
            'classical': 1,
            'blues': 0
        }
        complexity += style_complexity.get(request.style.value.lower(), 1)

        return min(10, max(1, complexity))

    async def _generate_reharmonization_variations(
        self,
        request: ReharmonizationRequest,
        original_reharmonization: list[ChordInfo]
    ) -> tuple[list[CreativeVariation], list[list[ChordInfo]]]:
        """Generate alternative reharmonization variations."""
        variations = []
        variations_data = []
        
        original_symbols = " - ".join(request.original_progression)
        
        # Conservative variation
        conservative_prompt = f"""Generate a CONSERVATIVE reharmonization of: {original_symbols}
Key: {request.key}, Style: {request.style.value}
Keep changes minimal - just add 7ths and smooth voice leading.
Return JSON: {{"progression": [{{"symbol": "Cmaj7", "notes": ["C", "E", "G", "B"], "midi_notes": [60, 64, 67, 71]}}]}}"""
        
        try:
            conservative_data = await self._generate_with_fallback(conservative_prompt, "reharm_conservative")
            if conservative_data and "progression" in conservative_data:
                variations.append(CreativeVariation(
                    label="Gentle Touch",
                    creativity_score=0.2,
                    description="Subtle enhancements - 7ths and smooth voice leading"
                ))
                variations_data.append([ChordInfo(**c) for c in conservative_data["progression"]])
        except Exception:
            pass
        
        # Bold variation
        bold_prompt = f"""Generate a BOLD, SURPRISING reharmonization of: {original_symbols}
Key: {request.key}, Style: {request.style.value}
Use tritone subs, secondary dominants, modal interchange. Be creative!
Return JSON: {{"progression": [{{"symbol": "Cmaj7", "notes": ["C", "E", "G", "B"], "midi_notes": [60, 64, 67, 71]}}]}}"""
        
        try:
            bold_data = await self._generate_with_fallback(bold_prompt, "reharm_bold")
            if bold_data and "progression" in bold_data:
                variations.append(CreativeVariation(
                    label="Complete Makeover",
                    creativity_score=0.9,
                    description="Dramatic transformation with advanced substitutions"
                ))
                variations_data.append([ChordInfo(**c) for c in bold_data["progression"]])
        except Exception:
            pass
        
        return variations, variations_data

    def _convert_to_chord_info(self, root: str, quality: str, original: dict) -> ChordInfo:
        """Convert Phase 6 chord data to ChordInfo schema"""
        from app.theory.chord_builder import get_chord_notes, chord_to_midi

        # Build chord symbol
        symbol = f"{root}{quality}"

        # Get notes and MIDI
        try:
            notes = get_chord_notes(root, quality)
            midi_notes = chord_to_midi(root, quality, octave=4)
        except Exception:
            # Fallback
            notes = [root]
            midi_notes = [60]  # Middle C

        # Determine function (simplified)
        function = original.get('function', '?')

        return ChordInfo(
            symbol=symbol,
            notes=notes,
            midi_notes=midi_notes,
            function=function,
            comment=f"Reharmonization of {original.get('root', '')}{original.get('quality', '')}"
        )

    def _generate_local_explanation(self, techniques: list, style: str) -> str:
        """Generate rule-based explanation for reharmonization"""
        if not techniques:
            return f"Applied standard {style} harmonic practices."

        technique_explanations = {
            'diatonic_substitution': 'diatonic chord substitutions',
            'modal_interchange': 'modal interchange borrowing',
            'tritone_substitution': 'tritone substitutions',
            'negative_harmony': 'negative harmony',
            'coltrane_changes': 'Coltrane changes',
            'common_tone_diminished': 'common tone diminished chords',
            'passing_chords': 'chromatic passing chords'
        }

        technique_names = [technique_explanations.get(t, t) for t in techniques]
        techniques_str = ', '.join(technique_names)

        return f"This reharmonization uses {techniques_str} to enhance the harmonic interest while maintaining {style} style characteristics and smooth voice leading."
    
    async def generate_voicings(self, request: VoicingRequest) -> VoicingResponse:
        """Generate chord voicing options"""
        prompt = f"""You are an expert piano voicing specialist.
Generate 4 different voicings for the chord: {request.chord}

Voicing style preference: {request.style.value}
Hand: {request.hand}
{'Include fingering suggestions' if request.include_fingering else ''}

Return a JSON object with this exact structure:
{{
    "voicings": [
        {{
            "name": "Basic shell voicing",
            "notes": ["C3", "E3", "G3", "B3"],
            "midi_notes": [48, 52, 55, 59],
            "fingering": [1, 2, 3, 5],
            "hand": "left"
        }}
    ],
    "tips": ["Tip for practicing voicings", "Another tip"]
}}

Guidelines:
- Provide 4 different voicing options from simple to complex
- Notes should be in order from lowest to highest
- MIDI notes should be in playable range (C2-C6, MIDI 36-84)
- Fingering: 1=thumb, 2=index, 3=middle, 4=ring, 5=pinky
- Include a variety: shell voicings, rootless, drop voicings, etc.

Return ONLY the JSON, no other text"""

        data = await self._generate_with_fallback(prompt, "voicing")

        return VoicingResponse(
            chord=request.chord,
            voicings=[VoicingInfo(**v) for v in data["voicings"]],
            tips=data.get("tips")
        )
    
    async def optimize_voice_leading(self, request: VoiceLeadingRequest) -> VoiceLeadingResponse:
        """Find optimal voice leading between two chords"""
        prompt = f"""You are an expert in voice leading and piano comping.
Find the optimal voice leading from {request.chord1} to {request.chord2}.
{'Style context: ' + request.style.value if request.style else ''}

Return a JSON object with this exact structure:
{{
    "chord1": {{
        "name": "Starting voicing for {request.chord1}",
        "notes": ["D3", "F3", "A3", "C4"],
        "midi_notes": [50, 53, 57, 60],
        "fingering": [1, 2, 3, 5],
        "hand": "left"
    }},
    "chord2": {{
        "name": "Target voicing for {request.chord2}",
        "notes": ["D3", "G3", "B3", "F4"],
        "midi_notes": [50, 55, 59, 65],
        "fingering": [1, 2, 4, 5],
        "hand": "left"
    }},
    "common_tones": ["D"],
    "movement": "Description of how each voice moves",
    "tips": ["Voice leading tip 1", "Tip 2"]
}}

Principles to follow:
- Minimize voice movement (stepwise motion preferred)
- Identify and hold common tones
- Avoid parallel 5ths/octaves
- Lead the 7th down to 3rd when possible

Return ONLY the JSON, no other text"""

        data = await self._generate_with_fallback(prompt, "voice_leading")

        return VoiceLeadingResponse(
            chord1=VoicingInfo(**data["chord1"]),
            chord2=VoicingInfo(**data["chord2"]),
            common_tones=data["common_tones"],
            movement=data["movement"],
            tips=data.get("tips")
        )
    

    async def generate_exercise(self, request: ExerciseRequest, template_id: Optional[str] = None) -> ExerciseResponse:
        """Generate a practice exercise"""
        
        # Template context injection
        template_context_str = ""
        engine_data = None
        
        if template_id:
            found_data = template_loader.find_exercise_by_id(template_id)
            if found_data:
                engine_data = found_data.get("engine_data") or found_data.get("musical_data")
                template_context_str = f"""
************************************************
STRICT TEMPLATE INSTRUCTION:
This exercise MUST be based on the following curriculum template:
TITLE: {found_data.get('name') or found_data.get('title')}
INSTRUCTION: {found_data.get('instructions') or found_data.get('pedagogy', {}).get('objective')}
PARAMETERS: {json.dumps(engine_data)}
************************************************
"""

        prompt = f"""You are an expert piano pedagogue and practice coach.
Create a practice exercise with these parameters:

Type: {request.type.value}
Key: {request.key}
Difficulty: {request.difficulty.value}
{'Focus area: ' + request.focus if request.focus else ''}
{template_context_str}

Return a JSON object with this exact structure:
{{
    "title": "Exercise title",
    "description": "What skill this exercise develops",
    "steps": [
        {{
            "instruction": "What to do in this step",
            "notes": ["C", "D", "E", "F", "G"],
            "midi_notes": [60, 62, 64, 65, 67],
            "duration": "quarter notes"
        }}
    ],
    "variations": ["Variation 1", "Variation 2 to make it harder"],
    "difficulty": "{request.difficulty.value}",
    "engine_data": {{ "optional": "raw data associated with exercise" }}
}}

Make the exercise:
- Practical and focused on real skills
- Progressive in difficulty within the exercise
- Include specific musical notation where helpful
- Provide 3-5 clear steps

Return ONLY the JSON, no other text"""

        data = await self._generate_with_fallback(prompt, "exercise")

        return ExerciseResponse(
            title=data["title"],
            description=data["description"],
            steps=[ExerciseStep(**step) for step in data["steps"]],
            variations=data.get("variations"),
            difficulty=data["difficulty"],
            engine_data=data.get("engine_data")
        )
    
    async def get_substitutions(self, request: SubstitutionRequest) -> SubstitutionResponse:
        """Get chord substitution options"""
        context_str = f" (context: {' - '.join(request.context)})" if request.context else ""
        
        prompt = f"""You are an expert jazz harmony teacher.
Suggest chord substitutions for: {request.chord}{context_str}

Style: {request.style.value}

Return a JSON object with this exact structure:
{{
    "substitutions": [
        {{
            "symbol": "Sub chord symbol",
            "notes": ["Note1", "Note2", "Note3"],
            "midi_notes": [48, 52, 55],
            "function": "Function explanation",
            "comment": "Why this substitution works"
        }}
    ],
    "explanations": {{
        "SubChord1": "Explanation why this sub works",
        "SubChord2": "Explanation for second sub"
    }}
}}

Include substitutions like:
- Tritone substitution (for dominants)
- Relative major/minor
- Modal interchange options
- Extended/altered versions
- Passing chord options

Provide 4-6 substitution options.
Return ONLY the JSON, no other text"""

        data = await self._generate_with_fallback(prompt, "substitution")

        return SubstitutionResponse(
            original=request.chord,
            substitutions=[ChordInfo(**sub) for sub in data["substitutions"]],
            explanations=data["explanations"]
        )

    def _generate_with_claude_cli(self, prompt: str) -> dict:
        """Generate content using Claude CLI (uses your existing subscription)"""
        if not self.claude_cli_available:
            raise ValueError("Claude CLI is not available")

        try:
            # Call claude CLI with the prompt (using --print for non-interactive mode)
            result = subprocess.run(
                ["claude", "--print", prompt],
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout for generation
            )

            if result.returncode != 0:
                raise ValueError(f"Claude CLI failed: {result.stderr}")

            # Parse the response
            return parse_json_from_response(result.stdout)

        except subprocess.TimeoutExpired:
            raise ValueError("Claude CLI request timed out")
        except Exception as e:
            raise ValueError(f"Claude CLI error: {str(e)}")

    def _generate_with_claude(self, prompt: str) -> dict:
        """Generate content using Claude (API or CLI)"""
        # Try API first if available
        if self.claude_api_available:
            response = self.claude.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=8096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            # Extract text from response
            text = response.content[0].text
            return parse_json_from_response(text)

        # Fall back to CLI if API not available
        elif self.claude_cli_available:
            return self._generate_with_claude_cli(prompt)

        else:
            raise ValueError("Claude is not available")

    def _load_mlx_model(self):
        """Lazy load MLX model"""
        if not self.mlx_model and self.mlx_available:
            print(f"Loading local MLX model: {self.mlx_model_path}...")
            self.mlx_model, self.mlx_tokenizer = load(self.mlx_model_path)
            print("✅ MLX model loaded")

    def _generate_with_mlx(self, prompt: str) -> dict:
        """Generate content using local MLX model"""
        if not self.mlx_available:
            raise ValueError("MLX is not available (install mlx-lm)")
        
        # Ensure model is loaded
        self._load_mlx_model()
        
        # Format prompt using the tokenizer's chat template
        messages = [{"role": "user", "content": prompt}]
        formatted_prompt = self.mlx_tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        response = generate(
            self.mlx_model, 
            self.mlx_tokenizer, 
            prompt=formatted_prompt, 
            max_tokens=2048, 
            verbose=True
        )
        
        return parse_json_from_response(response)

    async def _generate_with_fallback(self, prompt: str, operation_name: str = "generation") -> dict:
        """
        Generate content with automatic Gemini → Claude fallback

        Args:
            prompt: The prompt to send to the AI
            operation_name: Description for logging (e.g., "progression", "voicing")

        Returns:
            Parsed JSON response from the AI

        Raises:
            ValueError: If all AI providers fail or are unavailable
        """
        # Try Gemini first if available
        if self.gemini_available:
            try:
                response = self.model.generate_content(prompt)
                return parse_json_from_response(response.text)
            except Exception as gemini_error:
                error_str = str(gemini_error)
                # Check if it's a quota error
                if "429" in error_str or "quota" in error_str.lower():
                    print(f"⚠️  Gemini quota exceeded for {operation_name}, falling back to Claude...")
                    if not self.claude_api_available and not self.claude_cli_available:
                        raise ValueError(f"Gemini quota exceeded and Claude not available for {operation_name}")
                    # Fall through to Claude
                else:
                    # Re-raise non-quota errors
                    raise

        # Use Claude if Gemini not available or quota exceeded
        if self.claude_api_available or self.claude_cli_available:
            try:
                return self._generate_with_claude(prompt)
            except Exception as e:
                print(f"⚠️  Claude failed for {operation_name}: {e}")
                if not self.mlx_available:
                     raise
            
        # Fallback to Local MLX (Mac GPU)
        if self.mlx_available:
            print(f"⚠️  Cloud providers unavailable/limited for {operation_name}, falling back to Local MLX...")
            return self._generate_with_mlx(prompt)
            
        else:
            raise ValueError(f"No AI provider available for {operation_name}")

    async def generate_licks(self, request: LicksRequest) -> LicksResponse:
        """Generate jazz licks using hybrid AI + rules approach with Claude fallback"""

        # 1. Parse context (chord or progression)
        context_chords = (
            request.context.split()
            if request.context_type == ContextType.PROGRESSION
            else [request.context]
        )

        # 2. Get appropriate scales for context
        scales = lick_pattern_service.get_scales_for_context(
            context_chords,
            request.style.value
        )

        # 3. Build prompt with context
        prompt = self._build_licks_prompt(request, scales)

        # 4. Generate licks with retry logic and fallback
        max_retries = 2
        use_claude = False

        for attempt in range(max_retries):
            try:
                # Try Gemini first if available
                if self.gemini_available and not use_claude:
                    try:
                        response = self.model.generate_content(prompt)
                        data = parse_json_from_response(response.text)
                    except Exception as gemini_error:
                        error_str = str(gemini_error)
                        # Check if it's a quota error
                        if "429" in error_str or "quota" in error_str.lower():
                            print(f"⚠️  Gemini quota exceeded, falling back to Claude...")
                            use_claude = True
                            if not self.claude_api_available and not self.claude_cli_available:
                                raise ValueError("Gemini quota exceeded and Claude not available")
                            data = self._generate_with_claude(prompt)
                        else:
                            raise  # Re-raise non-quota errors
                # Use Claude if Gemini not available or quota exceeded
                elif self.claude_api_available or self.claude_cli_available:
                    data = self._generate_with_claude(prompt)
                else:
                    raise ValueError("No AI provider available")

                # 5. Validate each lick against pattern library
                validated_licks = []
                for lick_data in data.get("licks", []):
                    validation = lick_pattern_service.validate_lick(
                        lick_data,
                        context_chords,
                        request.style.value,
                        request.difficulty.value
                    )

                    if validation.is_valid:
                        validated_licks.append(LickInfo(**lick_data))

                # 6. If we have enough valid licks, return
                if len(validated_licks) >= 3:
                    if use_claude or not self.gemini_available:
                        provider = "Claude CLI (your subscription)" if self.claude_cli_available and not self.claude_api_available else "Claude API"
                    else:
                        provider = "Gemini"
                    print(f"✅ Generated {len(validated_licks)} licks using {provider}")
                    return LicksResponse(
                        context=request.context,
                        style=request.style.value,
                        difficulty=request.difficulty.value,
                        licks=validated_licks[:5],  # Max 5 licks
                        analysis=data.get("analysis", ""),
                        practice_tips=data.get("practice_tips", [])
                    )
            except Exception as e:
                if attempt == max_retries - 1:
                    raise ValueError(f"Could not generate valid licks: {str(e)}")

        # If validation fails after retries, raise error
        raise ValueError("Could not generate valid licks after retries")

    def _build_licks_prompt(self, request: LicksRequest, scales: list[str]) -> str:
        """Build detailed prompt for Gemini"""

        num_licks = 3 if request.difficulty == Difficulty.BEGINNER else 5

        prompt = f"""You are an expert jazz improviser and educator.
Generate {num_licks} jazz licks in {request.style.value} style.

Context: {request.context}
Context Type: {request.context_type.value}
Difficulty: {request.difficulty.value}
Length: {request.length_bars} bars (assume 4/4 time)

Appropriate scales for this context: {', '.join(scales)}

Guidelines for {request.style.value} style:
{self._get_style_guidelines(request.style)}

Difficulty guidelines for {request.difficulty.value}:
{self._get_difficulty_guidelines(request.difficulty)}

Return a JSON object with this exact structure:
{{
    "licks": [
        {{
            "name": "Descriptive lick name",
            "notes": ["C4", "D4", "E4", "G4", "F4", "E4"],
            "midi_notes": [60, 62, 64, 67, 65, 64],
            "fingering": [1, 2, 3, 5, 4, 3],
            "start_note": "C4",
            "end_note": "E4",
            "duration_beats": {request.length_bars * 4}.0,
            "style_tags": ["bebop", "descending", "chord_tones"],
            "theory_analysis": {{
                "chord_tones": [true, false, true, true, false, true],
                "scale_degrees": ["1", "2", "3", "5", "4", "3"],
                "approach_tones": ["D4 → diatonic approach to E4", "F4 → chromatic approach to E4"],
                "voice_leading": "Ascending stepwise motion targeting chord tones, then descending resolution",
                "harmonic_function": "Outlines Cmaj triad (C-E-G) with passing tones creating melodic interest"
            }}
        }}
    ],
    "analysis": "Explain how these licks work over the given context",
    "practice_tips": ["Tip 1", "Tip 2", "Tip 3"]
}}

For theory_analysis:
- chord_tones: Array of booleans indicating if each note is a chord tone (true) or passing/approach tone (false)
- scale_degrees: The scale degree of each note in relation to the root (use '1', 'b3', '#5', 'b7', etc.)
- approach_tones: List strings explaining chromatic or diatonic approaches (e.g., "B → chromatic approach to C")
- voice_leading: Describe the melodic contour (ascending, descending, stepwise, leaps, etc.)
- harmonic_function: Explain how the lick outlines the harmony (which chord tones, extensions, tensions)

CRITICAL RULES:
1. All notes MUST come from appropriate scales or chord tones
2. MIDI notes must be in range 48-84 (playable piano range)
3. Note names MUST include octave (e.g., "C4" not "C")
4. Duration must match length_bars * 4 beats = {request.length_bars * 4} beats
5. For bebop: use bebop scales, approach tones, target chord tones on strong beats
6. For blues: use blues scale, blue notes (b3, b5, b7), call-response patterns
7. For modern: use altered scales, wide intervals, unexpected note choices
8. For gospel: use pentatonic fills, chromatic runs, gospel turn-arounds

Return ONLY the JSON, no other text."""

        return prompt

    def _get_style_guidelines(self, style: LickStyle) -> str:
        """Get style-specific guidelines for prompt

        First tries to load from knowledge base documentation (if available),
        then falls back to hardcoded guidelines for backward compatibility.
        """
        # Try to get from knowledge base (documentation-first approach)
        try:
            from app.main import music_knowledge_base

            # Map LickStyle enum to knowledge base style names
            style_to_kb_map = {
                LickStyle.BEBOP: ("jazz", "bebop"),
                LickStyle.BLUES: ("jazz", "blues"),
                LickStyle.MODERN: ("jazz", "modern"),
                LickStyle.GOSPEL: ("gospel", "traditional"),
                LickStyle.SWING: ("jazz", "swing"),
                LickStyle.BOSSA: ("jazz", "bossa"),
            }

            if music_knowledge_base and music_knowledge_base.is_loaded():
                kb_style, kb_substyle = style_to_kb_map.get(style, ("jazz", None))
                kb_guidelines = music_knowledge_base.format_style_guidelines_for_prompt(kb_style, kb_substyle)

                # If we got comprehensive guidelines from docs, use them
                if kb_guidelines and len(kb_guidelines) > 100:
                    return kb_guidelines
        except Exception:
            # Knowledge base not available or error, fall back to hardcoded
            pass

        # Fallback: Hardcoded guidelines (backward compatible)
        guidelines = {
            LickStyle.BEBOP: """
- Use bebop scales (add passing tones between chord tones)
- Target chord tones on downbeats
- Use chromatic approach tones (half-step below or above target)
- Eighth-note based lines with swing feel
- Common patterns: enclosures, turn-arounds, ii-V-I lines""",

            LickStyle.BLUES: """
- Use blues scale (minor pentatonic + b5 blue note)
- Bend notes (grace notes before target)
- Call and response phrasing
- Blue notes on b3, b5, b7
- Repetition and variation""",

            LickStyle.MODERN: """
- Use altered scales, melodic minor modes
- Wide interval jumps (6ths, 7ths, octaves)
- Complex rhythms (triplets, quintuplets)
- Outside playing (resolve to inside)
- Angular, unexpected melodic contours""",

            LickStyle.GOSPEL: """
- Pentatonic fills and runs
- Chromatic passing tones
- Gospel turn-arounds (ending phrases)
- Grace notes and embellishments
- Rhythmic syncopation""",

            LickStyle.SWING: """
- Major scales and arpeggios
- Eighth-note swing feel
- Stepwise motion with occasional jumps
- Chord tone emphasis
- Clear, singable melodies""",

            LickStyle.BOSSA: """
- Lydian and Dorian modes
- Syncopated rhythms
- Smooth, flowing lines
- Extended chord tones (9ths, 11ths, 13ths)
- Latin rhythmic feel"""
        }
        return guidelines.get(style, "")

    def _get_difficulty_guidelines(self, difficulty: Difficulty) -> str:
        """Get difficulty-specific guidelines

        First tries to load from knowledge base documentation (if available),
        then falls back to hardcoded guidelines for backward compatibility.
        """
        # Try to get from knowledge base (documentation-first approach)
        try:
            from app.main import music_knowledge_base

            if music_knowledge_base and music_knowledge_base.is_loaded():
                # Get difficulty calibration template from knowledge base
                difficulty_template = music_knowledge_base.get_prompt_template("difficulty", difficulty.value)

                # If we got specific difficulty guidelines from docs, format them
                if difficulty_template and "characteristics" in difficulty_template:
                    characteristics = difficulty_template["characteristics"]
                    return "\n".join(f"- {char}" for char in characteristics)
        except Exception:
            # Knowledge base not available or error, fall back to hardcoded
            pass

        # Fallback: Hardcoded guidelines (backward compatible)
        guidelines = {
            Difficulty.BEGINNER: """
- Stepwise motion (mostly 2nds, occasional 3rds)
- Simple rhythms (quarter and eighth notes)
- Stay within 1 octave range
- Clear, singable melodies
- 4-8 notes per bar maximum""",

            Difficulty.INTERMEDIATE: """
- Mix stepwise and skipwise motion (up to 5ths)
- Eighth notes with occasional 16th note pairs
- 1-1.5 octave range
- Some chromatic passing tones
- 6-12 notes per bar""",

            Difficulty.ADVANCED: """
- Wide intervals (6ths, 7ths, octaves)
- Complex rhythms (16th notes, triplets, syncopation)
- 2+ octave range
- Extensive chromaticism
- 10+ notes per bar possible"""
        }
        return guidelines.get(difficulty, "")

    def _get_arranger_for_style(self, style: str):
        """Get the appropriate arranger for a style"""
        style_to_arranger = {
            "jazz": JazzArranger(),
            "gospel": GospelArranger(),
            "neo_soul": NeosoulArranger(),
            "blues": BluesArranger(),
            "classical": ClassicalArranger(),
            "pop": JazzArranger(),  # Use jazz arranger for pop
            "rnb": NeosoulArranger(),  # Use neosoul arranger for R&B
        }
        return style_to_arranger.get(style.lower(), JazzArranger())

    async def arrange_progression(self, request: ArrangeRequest) -> ArrangeResponse:
        """Convert chord progression to full MIDI arrangement"""
        try:
            # Determine style-specific arranger
            if request.style.value.lower() == "gospel" and MLX_AVAILABLE:
                # Use Advanced MLX Generator for Gospel
                if not hasattr(self, 'gospel_generator') or self.gospel_generator is None:
                    from app.gospel.ai.mlx_music_generator import MLXGospelGenerator
                    print("🎹 Initializing Advanced MLX Gospel Generator...")
                    self.gospel_generator = MLXGospelGenerator()
                
                print(f"🤖 Generating gospel arrangement with Qwen2.5-14B (Style: {request.style.value})...")
                arrangement = self.gospel_generator.generate_arrangement(
                    chord_progression=request.chords,
                    key=request.key,
                    tempo=request.tempo,
                    application=request.application or "worship",
                    num_bars=32 # Better defaulting for full songs
                )
            else:
                # Use standard rule-based arrangers
                arranger = self._get_arranger_for_style(request.style.value)

                # Determine default application if not provided
                default_apps = {
                    "jazz": "standard",
                    "gospel": "uptempo", # Fallback if MLX not available
                    "neo_soul": "smooth",
                    "blues": "shuffle",
                    "classical": "classical",
                }
                application = request.application or default_apps.get(request.style.value, "standard")

                # Generate arrangement
                arrangement = arranger.arrange_progression(
                    chords=request.chords,
                    key=request.key,
                    bpm=request.tempo,
                    application=application,
                    time_signature=request.time_signature
                )

            # Export to MIDI
            output_dir = settings.OUTPUTS_DIR / "ai_generated"
            output_dir.mkdir(parents=True, exist_ok=True)

            import time
            filename = f"ai_{request.style.value}_{request.key}_{request.tempo}bpm_{int(time.time())}.mid"
            midi_path = output_dir / filename

            export_enhanced_midi(arrangement, midi_path)

            # Read MIDI file as base64
            with open(midi_path, 'rb') as f:
                midi_base64 = base64.b64encode(f.read()).decode('utf-8')

            return ArrangeResponse(
                success=True,
                midi_file_path=str(midi_path),
                midi_base64=midi_base64,
                arrangement_info={
                    "tempo": arrangement.tempo,
                    "key": arrangement.key,
                    "time_signature": f"{arrangement.time_signature[0]}/{arrangement.time_signature[1]}",
                    "total_bars": arrangement.total_bars,
                    "total_notes": len(arrangement.left_hand_notes) + len(arrangement.right_hand_notes),
                    "left_hand_notes": len(arrangement.left_hand_notes),
                    "right_hand_notes": len(arrangement.right_hand_notes),
                    "duration_seconds": round(arrangement.total_duration_seconds, 2),
                    "application": arrangement.application,
                }
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            return ArrangeResponse(success=False, error=str(e))


# Global service instance
ai_generator_service = AIGeneratorService()
