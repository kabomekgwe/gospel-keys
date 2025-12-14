"""Neo-Soul Piano Generation Service - Gemini + Rule-Based Arranger"""

import base64
import re
from pathlib import Path
from typing import Optional, List, Tuple
import google.generativeai as genai

from app.core.config import settings
from app.schemas.neosoul import (
    GenerateNeosoulRequest,
    GenerateNeosoulResponse,
    ChordAnalysis,
    MIDINoteInfo,
    NeosoulGeneratorStatus,
)
from app.neosoul.arrangement.arranger import NeosoulArranger
from app.gospel.midi.enhanced_exporter import export_enhanced_midi
from app.gospel import Arrangement


# Configure Gemini
if settings.google_api_key:
    genai.configure(api_key=settings.google_api_key)


class NeosoulGeneratorService:
    """
    Neo-soul piano generation service.

    Pipeline:
    1. Gemini API generates chord progression from natural language
    2. NeosoulArranger creates MIDI arrangement (rule-based)
    3. Export to MIDI file

    Falls back gracefully if any component unavailable.
    """

    def __init__(self):
        """Initialize neo-soul generation service."""
        self.gemini_model = None
        self.arranger = None

        # Initialize Gemini
        if settings.google_api_key:
            try:
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
                print("✅ Gemini API initialized for Neo-Soul")
            except Exception as e:
                print(f"⚠️  Gemini initialization failed: {e}")

        # Initialize arranger (rule-based)
        try:
            self.arranger = NeosoulArranger()
            print("✅ Neo-Soul arranger initialized")
        except Exception as e:
            print(f"❌ Neo-Soul arranger failed: {e}")
            raise

    def get_status(self) -> NeosoulGeneratorStatus:
        """Get current status of neo-soul generation system."""
        return NeosoulGeneratorStatus(
            gemini_available=self.gemini_model is not None,
            rules_available=self.arranger is not None,
            ready_for_production=(self.gemini_model is not None and self.arranger is not None)
        )

    async def generate_neosoul_arrangement(
        self,
        request: GenerateNeosoulRequest
    ) -> GenerateNeosoulResponse:
        """
        Generate complete neo-soul piano arrangement from natural language.

        Args:
            request: Generation parameters

        Returns:
            GenerateNeosoulResponse with MIDI file and metadata
        """
        try:
            # Step 1: Generate chord progression using Gemini
            if self.gemini_model and request.include_progression:
                print("🎵 Generating neo-soul chord progression with Gemini...")
                chords, key, tempo, analysis = await self._generate_progression_with_gemini(
                    request.description,
                    request.key,
                    request.tempo,
                    request.num_bars
                )
            else:
                # Fallback: parse description for chords
                print("📝 Parsing description for chords (Gemini unavailable)...")
                chords, key, tempo = self._parse_description_fallback(
                    request.description,
                    request.key,
                    request.tempo
                )
                analysis = []

            # Step 2: Generate MIDI arrangement
            print(f"🎹 Generating neo-soul arrangement ({request.application.value})...")
            arrangement = self.arranger.arrange_progression(
                chords=chords,
                key=key,
                bpm=tempo,
                application=request.application.value,
                time_signature=(4, 4)
            )

            # Step 3: Export to MIDI
            print("💾 Exporting to MIDI...")
            midi_path, midi_base64 = self._export_to_midi(arrangement)

            # Step 4: Build response
            return GenerateNeosoulResponse(
                success=True,
                midi_file_path=str(midi_path),
                midi_base64=midi_base64,
                progression=analysis if request.include_progression else None,
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
                },
                notes_preview=self._get_notes_preview(arrangement),
                generation_method="gemini+rules"
            )

        except Exception as e:
            print(f"❌ Neo-soul generation failed: {e}")
            import traceback
            traceback.print_exc()
            return GenerateNeosoulResponse(
                success=False,
                generation_method="failed",
                error=str(e)
            )

    async def _generate_progression_with_gemini(
        self,
        description: str,
        key: Optional[str],
        tempo: Optional[int],
        num_bars: int
    ) -> Tuple[List[str], str, int, List[ChordAnalysis]]:
        """Generate neo-soul chord progression using Gemini API."""
        # Build prompt
        prompt = f"""You are an expert neo-soul pianist and music theorist.

Generate a {num_bars}-bar neo-soul piano chord progression based on this description:
"{description}"

{"Key: " + key if key else "Choose an appropriate key"}
{"Tempo: " + str(tempo) + " BPM" if tempo else "Choose an appropriate tempo"}

Requirements:
- Use extended neo-soul harmony (9ths, 11ths, 13ths, add9, sus2/4)
- Include chromatic movement and modal interchange
- Rich, sophisticated voicings (maj7#11, m11, etc.)
- Influences: D'Angelo, Erykah Badu, Robert Glasper

Return ONLY valid JSON with this exact structure:
{{
  "key": "Dm",
  "tempo": 85,
  "chords": [
    {{
      "symbol": "Dm9",
      "function": "i9",
      "notes": ["D", "F", "A", "C", "E"],
      "comment": "Minor 9th with laid-back feel"
    }}
  ]
}}

Generate {num_bars} chords total. Each chord should have symbol, function, notes, and comment."""

        response = self.gemini_model.generate_content(prompt)

        # Parse JSON from response
        import json
        response_text = response.text.strip()

        # Extract JSON (handle code blocks)
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            json_text = json_match.group(1)
        else:
            # Try direct parse
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            json_text = json_match.group(0) if json_match else response_text

        data = json.loads(json_text)

        # Extract data
        generated_key = data.get("key", key or "Dm")
        generated_tempo = data.get("tempo", tempo or 85)
        chord_data = data.get("chords", [])

        # Build chord list and analysis
        chords = [c["symbol"] for c in chord_data]
        analysis = [
            ChordAnalysis(
                symbol=c["symbol"],
                function=c.get("function", ""),
                notes=c.get("notes", []),
                comment=c.get("comment")
            )
            for c in chord_data
        ]

        return chords, generated_key, generated_tempo, analysis

    def _parse_description_fallback(
        self,
        description: str,
        key: Optional[str],
        tempo: Optional[int]
    ) -> Tuple[List[str], str, int]:
        """Fallback: parse description without Gemini."""
        # Extract key if present
        key_match = re.search(r'\b([A-G][#b]?)\s*(major|minor|m)?\b', description, re.IGNORECASE)
        parsed_key = key or (key_match.group(1) if key_match else "Dm")

        # Extract tempo
        tempo_match = re.search(r'\b(\d{2,3})\s*bpm\b', description, re.IGNORECASE)
        parsed_tempo = tempo or (int(tempo_match.group(1)) if tempo_match else 85)

        # Default neo-soul progression (modal, extended chords)
        chords = ["Dm9", "Em11", "Fmaj7#11", "Am9"]

        return chords, parsed_key, parsed_tempo

    def _export_to_midi(self, arrangement: Arrangement) -> Tuple[Path, str]:
        """Export arrangement to MIDI file."""
        # Create output directory
        output_dir = settings.OUTPUTS_DIR / "neosoul_generated"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        import time
        timestamp = int(time.time())
        filename = f"neosoul_{arrangement.key}_{arrangement.tempo}bpm_{timestamp}.mid"
        midi_path = output_dir / filename

        # Export
        export_enhanced_midi(arrangement, midi_path)

        # Read and encode as base64
        with open(midi_path, 'rb') as f:
            midi_bytes = f.read()
            midi_base64 = base64.b64encode(midi_bytes).decode('utf-8')

        return midi_path, midi_base64

    def _get_notes_preview(self, arrangement: Arrangement, bars: int = 4) -> List[MIDINoteInfo]:
        """Get preview of first N bars for visualization."""
        beats_per_bar = arrangement.time_signature[0]
        max_time = bars * beats_per_bar

        all_notes = arrangement.get_all_notes()
        preview_notes = [n for n in all_notes if n.time < max_time]

        return [
            MIDINoteInfo(
                pitch=note.pitch,
                time=note.time,
                duration=note.duration,
                velocity=note.velocity,
                hand=note.hand
            )
            for note in preview_notes[:100]  # Limit to 100 notes for preview
        ]


# Global service instance
neosoul_generator_service = NeosoulGeneratorService()
