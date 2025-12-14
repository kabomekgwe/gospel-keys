"""Gospel Piano Generation Service - Gemini + MLX Hybrid"""

import base64
import re
from pathlib import Path
from typing import Optional, List, Tuple
import google.generativeai as genai

from app.core.config import settings
from app.schemas.gospel import (
    GenerateGospelRequest,
    GenerateGospelResponse,
    ChordAnalysis,
    MIDINoteInfo,
    GospelGeneratorStatus,
)
from app.gospel.arrangement.hybrid_arranger import HybridGospelArranger
from app.gospel.arrangement.arranger import GospelArranger
from app.gospel.midi.enhanced_exporter import export_enhanced_midi
from app.gospel import Arrangement


# Configure Gemini
if settings.google_api_key:
    genai.configure(api_key=settings.google_api_key)


class GospelGeneratorService:
    """
    Hybrid gospel piano generation service.

    Pipeline:
    1. Gemini API generates chord progression from natural language
    2. HybridGospelArranger creates MIDI arrangement (MLX or rules)
    3. Export to MIDI file

    Falls back gracefully if any component unavailable.
    """

    def __init__(self):
        """Initialize gospel generation service."""
        self.gemini_model = None
        self.hybrid_arranger = None
        self.rule_arranger = None

        # Initialize Gemini
        if settings.google_api_key:
            try:
                self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
                print("✅ Gemini API initialized")
            except Exception as e:
                print(f"⚠️  Gemini initialization failed: {e}")

        # Initialize arrangers (rule-based always available as fallback)
        try:
            self.rule_arranger = GospelArranger()
            print("✅ Rule-based arranger initialized")
        except Exception as e:
            print(f"❌ Rule-based arranger failed: {e}")
            raise

    def get_status(self) -> GospelGeneratorStatus:
        """Get current status of gospel generation system."""
        # Check if MLX is available
        mlx_available = False
        mlx_trained = False
        try:
            from app.gospel.ai.mlx_music_generator import MLXGospelGenerator
            mlx_available = True
            # Check for trained checkpoint
            checkpoint_path = Path("checkpoints/mlx-gospel/best")
            mlx_trained = checkpoint_path.exists()
        except Exception:
            pass

        # Check dataset size
        dataset_path = Path("data/gospel_dataset/validated")
        dataset_size = len(list(dataset_path.glob("*.mid"))) if dataset_path.exists() else 0

        # Determine recommended AI percentage
        if mlx_trained and dataset_size >= 100:
            recommended_ai = 0.8  # Highly trained
        elif mlx_trained and dataset_size >= 50:
            recommended_ai = 0.5  # Moderately trained
        elif mlx_available:
            recommended_ai = 0.2  # Pretrained only
        else:
            recommended_ai = 0.0  # Rules only

        return GospelGeneratorStatus(
            mlx_available=mlx_available,
            mlx_trained=mlx_trained,
            gemini_available=self.gemini_model is not None,
            recommended_ai_percentage=recommended_ai,
            dataset_size=dataset_size,
            ready_for_production=(mlx_trained and dataset_size >= 100)
        )

    async def generate_gospel_arrangement(
        self,
        request: GenerateGospelRequest
    ) -> GenerateGospelResponse:
        """
        Generate complete gospel piano arrangement from natural language.

        Args:
            request: Generation parameters

        Returns:
            GenerateGospelResponse with MIDI file and metadata
        """
        try:
            # Step 1: Generate chord progression using Gemini
            if self.gemini_model and request.include_progression:
                print("🎵 Generating chord progression with Gemini...")
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
            print(f"🎹 Generating arrangement (AI: {request.ai_percentage * 100}%)...")
            arranger = self._get_arranger(request.ai_percentage)
            arrangement = arranger.arrange_progression(
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
            return GenerateGospelResponse(
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
                generation_method=self._determine_generation_method(request.ai_percentage)
            )

        except Exception as e:
            print(f"❌ Generation failed: {e}")
            import traceback
            traceback.print_exc()
            return GenerateGospelResponse(
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
        """Generate chord progression using Gemini API."""
        # Build prompt
        prompt = f"""You are an expert gospel piano arranger and music theorist.

Generate a {num_bars}-bar gospel piano chord progression based on this description:
"{description}"

{"Key: " + key if key else "Choose an appropriate key"}
{"Tempo: " + str(tempo) + " BPM" if tempo else "Choose an appropriate tempo"}

Requirements:
- Use extended gospel harmony (9ths, 11ths, 13ths)
- Include chromatic passing chords
- Authentic gospel voice leading
- Rich harmonic movement

Return ONLY valid JSON with this exact structure:
{{
  "key": "C",
  "tempo": 72,
  "chords": [
    {{
      "symbol": "Cmaj9",
      "function": "I",
      "notes": ["C", "E", "G", "B", "D"],
      "comment": "Tonic with added 9th"
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
        generated_key = data.get("key", key or "C")
        generated_tempo = data.get("tempo", tempo or 72)
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
        parsed_key = key or (key_match.group(1) if key_match else "C")

        # Extract tempo
        tempo_match = re.search(r'\b(\d{2,3})\s*bpm\b', description, re.IGNORECASE)
        parsed_tempo = tempo or (int(tempo_match.group(1)) if tempo_match else 72)

        # Default gospel progression (I-IV-V-vi)
        if "major" in description.lower() or not any(x in description.lower() for x in ["minor", "m"]):
            chords = [f"{parsed_key}maj7", f"{parsed_key}maj9", "Fmaj7", "G7", "Am7"]
        else:
            chords = [f"{parsed_key}m7", f"{parsed_key}m9", "Dm7", "Em7", "Am7"]

        return chords[:4], parsed_key, parsed_tempo

    def _get_arranger(self, ai_percentage: float):
        """Get appropriate arranger based on AI percentage."""
        if ai_percentage > 0:
            # Try to initialize hybrid arranger if not already done
            if self.hybrid_arranger is None:
                try:
                    self.hybrid_arranger = HybridGospelArranger(
                        ai_percentage=ai_percentage,
                        fallback_to_rules=True
                    )
                except Exception as e:
                    print(f"⚠️  Hybrid arranger init failed: {e}, using rules")
                    return self.rule_arranger

            # Update AI percentage if arranger already exists
            self.hybrid_arranger.ai_percentage = ai_percentage
            return self.hybrid_arranger
        else:
            return self.rule_arranger

    def _export_to_midi(self, arrangement: Arrangement) -> Tuple[Path, str]:
        """Export arrangement to MIDI file."""
        # Create output directory
        output_dir = settings.OUTPUTS_DIR / "gospel_generated"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        import time
        timestamp = int(time.time())
        filename = f"gospel_{arrangement.key}_{arrangement.tempo}bpm_{timestamp}.mid"
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

    def _determine_generation_method(self, ai_percentage: float) -> str:
        """Determine which generation method was used."""
        if ai_percentage == 0.0:
            return "gemini+rules"
        elif ai_percentage == 1.0:
            return "gemini+mlx"
        else:
            return "gemini+hybrid"


# Global service instance
gospel_generator_service = GospelGeneratorService()
