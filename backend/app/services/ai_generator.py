"""AI Music Theory Generator Service using Google Gemini"""

import json
import os
import re
from typing import Optional

import google.generativeai as genai

from app.schemas.ai import (
    ProgressionRequest, ProgressionResponse, ChordInfo,
    ReharmonizationRequest, ReharmonizationResponse,
    VoicingRequest, VoicingResponse, VoicingInfo,
    VoiceLeadingRequest, VoiceLeadingResponse,
    ExerciseRequest, ExerciseResponse, ExerciseStep,
    SubstitutionRequest, SubstitutionResponse,
    GeneratorInfo, GeneratorsListResponse, GeneratorCategory,
)
from app.core.config import settings


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


class AIGeneratorService:
    """Service for AI-powered music theory generation using Gemini"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-flash-latest')
    
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

        response = self.model.generate_content(prompt)
        data = parse_json_from_response(response.text)
        
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

        response = self.model.generate_content(prompt)
        data = parse_json_from_response(response.text)
        
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

        response = self.model.generate_content(prompt)
        data = parse_json_from_response(response.text)
        
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

        response = self.model.generate_content(prompt)
        data = parse_json_from_response(response.text)
        
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

        response = self.model.generate_content(prompt)
        data = parse_json_from_response(response.text)
        
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

        response = self.model.generate_content(prompt)
        data = parse_json_from_response(response.text)
        
        return SubstitutionResponse(
            original=request.chord,
            substitutions=[ChordInfo(**sub) for sub in data["substitutions"]],
            explanations=data["explanations"]
        )


# Global service instance
ai_generator_service = AIGeneratorService()
