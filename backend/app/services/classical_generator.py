"""Classical Piano Generation Service"""
import base64, re
from pathlib import Path
from typing import Optional, List, Tuple
import google.generativeai as genai
from app.core.config import settings
from app.schemas.classical import *
from app.classical.arrangement.arranger import ClassicalArranger
from app.gospel.midi.enhanced_exporter import export_enhanced_midi
from app.gospel import Arrangement

if settings.google_api_key:
    genai.configure(api_key=settings.google_api_key)

class ClassicalGeneratorService:
    def __init__(self):
        self.gemini_model = None
        self.arranger = None
        if settings.google_api_key:
            try:
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                print("✅ Gemini API initialized for Classical")
            except Exception as e:
                print(f"⚠️  Gemini initialization failed: {e}")
        try:
            self.arranger = ClassicalArranger()
            print("✅ Classical arranger initialized")
        except Exception as e:
            print(f"❌ Classical arranger failed: {e}")
            raise

    def get_status(self) -> ClassicalGeneratorStatus:
        return ClassicalGeneratorStatus(
            gemini_available=self.gemini_model is not None,
            rules_available=self.arranger is not None,
            ready_for_production=(self.gemini_model is not None and self.arranger is not None)
        )

    async def generate_classical_arrangement(self, request: GenerateClassicalRequest) -> GenerateClassicalResponse:
        try:
            if self.gemini_model and request.include_progression:
                chords, key, tempo, analysis = await self._generate_progression_with_gemini(
                    request.description, request.key, request.tempo, request.num_bars, request.application)
            else:
                chords, key, tempo = self._parse_description_fallback(
                    request.description, request.key, request.tempo, request.application)
                analysis = []
            
            arrangement = self.arranger.arrange_progression(
                chords=chords, key=key, bpm=tempo,
                application=request.application.value, time_signature=request.time_signature)
            
            midi_path, midi_base64 = self._export_to_midi(arrangement)
            
            return GenerateClassicalResponse(
                success=True, midi_file_path=str(midi_path), midi_base64=midi_base64,
                progression=analysis if request.include_progression else None,
                arrangement_info={
                    "tempo": arrangement.tempo, "key": arrangement.key,
                    "time_signature": f"{arrangement.time_signature[0]}/{arrangement.time_signature[1]}",
                    "total_bars": arrangement.total_bars,
                    "total_notes": len(arrangement.left_hand_notes) + len(arrangement.right_hand_notes),
                    "left_hand_notes": len(arrangement.left_hand_notes),
                    "right_hand_notes": len(arrangement.right_hand_notes),
                    "duration_seconds": round(arrangement.total_duration_seconds, 2),
                    "application": arrangement.application,
                },
                notes_preview=self._get_notes_preview(arrangement),
                generation_method="gemini+rules")
        except Exception as e:
            import traceback; traceback.print_exc()
            return GenerateClassicalResponse(success=False, generation_method="failed", error=str(e))

    async def _generate_progression_with_gemini(self, description, key, tempo, num_bars, application):
        period_info = {
            "baroque": "Baroque period (1600-1750) - counterpoint, fugal, ornate",
            "classical": "Classical period (1750-1820) - balanced, elegant, I-IV-V-I",
            "romantic": "Romantic period (1820-1900) - expressive, chromatic harmony"
        }
        prompt = f"""Generate a {num_bars}-bar classical {application.value} period progression.
Period: {period_info.get(application.value, "Classical")}
Description: "{description}"
{f"Key: {key}" if key else "Choose key"}
{f"Tempo: {tempo} BPM" if tempo else "Choose tempo"}
Return JSON: {{"key": "C", "tempo": 120, "chords": [{{"symbol": "C", "function": "I", "notes": ["C","E","G"], "comment": "Tonic"}}]}}
Generate {num_bars} chords following classical harmony rules."""
        response = self.gemini_model.generate_content(prompt)
        import json
        response_text = response.text.strip()
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
        json_text = json_match.group(1) if json_match else response_text
        data = json.loads(json_text)
        chords = [c["symbol"] for c in data.get("chords", [])]
        analysis = [ChordAnalysis(**c) for c in data.get("chords", [])]
        return chords, data.get("key", key or "C"), data.get("tempo", tempo or 120), analysis

    def _parse_description_fallback(self, description, key, tempo, application):
        parsed_key = key or "C"
        parsed_tempo = tempo or 120
        # Default classical progression (I-IV-V-I)
        if application == ClassicalApplication.BAROQUE:
            chords = ["Dm", "Am", "Bb", "F", "Gm", "Dm", "A7", "Dm"]  # Baroque in D minor
        elif application == ClassicalApplication.ROMANTIC:
            chords = ["C", "Am", "F", "G", "Em", "Am", "Dm", "G7"]  # Romantic progression
        else:
            chords = ["C", "F", "G", "C", "Am", "Dm", "G", "C"]  # Classical I-IV-V-I
        return chords[:num_bars] if 'num_bars' in locals() else chords[:8], parsed_key, parsed_tempo

    def _export_to_midi(self, arrangement):
        output_dir = settings.OUTPUTS_DIR / "classical_generated"
        output_dir.mkdir(parents=True, exist_ok=True)
        import time
        filename = f"classical_{arrangement.application}_{arrangement.key}_{arrangement.tempo}bpm_{int(time.time())}.mid"
        midi_path = output_dir / filename
        export_enhanced_midi(arrangement, midi_path)
        with open(midi_path, 'rb') as f:
            midi_base64 = base64.b64encode(f.read()).decode('utf-8')
        return midi_path, midi_base64

    def _get_notes_preview(self, arrangement, bars=4):
        max_time = bars * arrangement.time_signature[0]
        preview_notes = [n for n in arrangement.get_all_notes() if n.time < max_time]
        return [MIDINoteInfo(pitch=n.pitch, time=n.time, duration=n.duration,
                velocity=n.velocity, hand=n.hand) for n in preview_notes[:100]]

classical_generator_service = ClassicalGeneratorService()
