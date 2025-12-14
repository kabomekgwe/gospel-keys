"""AI Music Theory Generator Service using Google Gemini with Claude fallback"""

import json
import os
import re
import subprocess
from typing import Optional

import google.generativeai as genai
from anthropic import Anthropic

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
)
from app.core.config import settings
from app.jazz.lick_patterns import lick_pattern_service


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

        # Ensure at least one AI provider is available
        if not self.gemini_available and not self.claude_api_available and not self.claude_cli_available:
            raise ValueError("No AI provider available. Please set GOOGLE_API_KEY, ANTHROPIC_API_KEY, or ensure 'claude' CLI is installed")
    
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
    
    async def generate_progression(self, request: ProgressionRequest) -> ProgressionResponse:
        """Generate a chord progression using Gemini"""
        prompt = f"""You are an expert music theory teacher and jazz piano player.
Generate a {request.length}-chord progression in the key of {request.key} {request.mode}.

Style: {request.style.value}
{'Mood: ' + request.mood.value if request.mood else ''}
{'Include extended chords (7ths, 9ths, 11ths, 13ths)' if request.include_extensions else 'Use basic triads only'}

Return a JSON object with this exact structure:
{{
    "progression": [
        {{
            "symbol": "Cmaj7",
            "notes": ["C", "E", "G", "B"],
            "midi_notes": [60, 64, 67, 71],
            "function": "I",
            "comment": "Tonic chord, establishes the key"
        }}
    ],
    "analysis": "Brief analysis of why this progression works",
    "tips": ["Tip 1 for playing this progression", "Tip 2"]
}}

Make sure:
1. The progression sounds authentic to the {request.style.value} style
2. Each chord has correct notes and MIDI numbers
3. Include roman numeral analysis for each chord function
4. MIDI notes should be in a playable piano range (C3-C6, MIDI 48-84)
5. Return ONLY the JSON, no other text"""

        data = await self._generate_with_fallback(prompt, "progression")

        return ProgressionResponse(
            progression=[ChordInfo(**chord) for chord in data["progression"]],
            key=request.key,
            style=request.style.value,
            analysis=data.get("analysis"),
            tips=data.get("tips")
        )
    
    async def generate_reharmonization(self, request: ReharmonizationRequest) -> ReharmonizationResponse:
        """Generate reharmonization suggestions"""
        original = " - ".join(request.original_progression)
        
        prompt = f"""You are an expert jazz arranger and reharmonization specialist.
Reharmonize this chord progression in {request.style.value} style:

Original progression: {original}
Key: {request.key}

Return a JSON object with this exact structure:
{{
    "reharmonized": [
        {{
            "symbol": "Cmaj9",
            "notes": ["C", "E", "G", "B", "D"],
            "midi_notes": [48, 52, 55, 59, 62],
            "function": "I",
            "comment": "Extended from Cmaj7"
        }}
    ],
    "explanation": "Detailed explanation of the reharmonization approach",
    "techniques_used": ["tritone substitution", "secondary dominants", "etc."]
}}

Apply appropriate reharmonization techniques for {request.style.value} style:
- Jazz: tritone subs, passing diminished, ii-V chains
- Gospel: chromatic mediants, extended gospel moves, plagal cadences
- Neo-soul: minor 11ths, altered dominants, modal interchange

Return ONLY the JSON, no other text"""

        data = await self._generate_with_fallback(prompt, "reharmonization")

        return ReharmonizationResponse(
            original=request.original_progression,
            reharmonized=[ChordInfo(**chord) for chord in data["reharmonized"]],
            explanation=data["explanation"],
            techniques_used=data["techniques_used"]
        )
    
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
    
    async def generate_exercise(self, request: ExerciseRequest) -> ExerciseResponse:
        """Generate a practice exercise"""
        prompt = f"""You are an expert piano pedagogue and practice coach.
Create a practice exercise with these parameters:

Type: {request.type.value}
Key: {request.key}
Difficulty: {request.difficulty.value}
{'Focus area: ' + request.focus if request.focus else ''}

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
    "difficulty": "{request.difficulty.value}"
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
            difficulty=data["difficulty"]
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
            return self._generate_with_claude(prompt)
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
        """Get style-specific guidelines for prompt"""
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
        """Get difficulty-specific guidelines"""
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


# Global service instance
ai_generator_service = AIGeneratorService()
