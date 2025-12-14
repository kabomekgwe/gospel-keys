"""Blues Piano Generation Service"""
import base64, re
from pathlib import Path
from typing import Optional, List, Tuple
import google.generativeai as genai
from app.core.config import settings
from app.schemas.blues import *
from app.blues.arrangement.arranger import BluesArranger
from app.gospel.midi.enhanced_exporter import export_enhanced_midi
from app.gospel import Arrangement

if settings.google_api_key:
    genai.configure(api_key=settings.google_api_key)

class BluesGeneratorService:
    def __init__(self):
        self.gemini_model = None
        self.arranger = None
        if settings.google_api_key:
            try:
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                print("✅ Gemini API initialized for Blues")
            except Exception as e:
                print(f"⚠️  Gemini initialization failed: {e}")
        try:
            self.arranger = BluesArranger()
            print("✅ Blues arranger initialized")
        except Exception as e:
            print(f"❌ Blues arranger failed: {e}")
            raise

    def get_status(self) -> BluesGeneratorStatus:
        return BluesGeneratorStatus(
            gemini_available=self.gemini_model is not None,
            rules_available=self.arranger is not None,
            ready_for_production=(self.gemini_model is not None and self.arranger is not None)
        )

    async def generate_blues_arrangement(self, request: GenerateBluesRequest) -> GenerateBluesResponse:
        try:
            if self.gemini_model and request.include_progression:
                chords, key, tempo, analysis = await self._generate_progression_with_gemini(
                    request.description, request.key, request.tempo, request.num_bars)
            else:
                chords, key, tempo = self._parse_description_fallback(
                    request.description, request.key, request.tempo)
                analysis = []
            
            arrangement = self.arranger.arrange_progression(
                chords=chords, key=key, bpm=tempo,
                application=request.application.value, time_signature=(4, 4))
            
            midi_path, midi_base64 = self._export_to_midi(arrangement)
            
            return GenerateBluesResponse(
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
            return GenerateBluesResponse(success=False, generation_method="failed", error=str(e))

    async def _generate_progression_with_gemini(self, description, key, tempo, num_bars):
        prompt = f"""Generate a {num_bars}-bar blues progression (typically 12-bar blues: I-I-I-I-IV-IV-I-I-V-IV-I-I).
Description: "{description}"
{"Key: " + key if key else "Choose key"}
{"Tempo: " + str(tempo) + " BPM" if tempo else "Choose tempo"}
Return JSON: {{"key": "E", "tempo": 100, "chords": [{{"symbol": "E7", "function": "I7", "notes": ["E","G#","B","D"], "comment": "Tonic dom 7th"}}]}}
Generate {num_bars} chords."""
        response = self.gemini_model.generate_content(prompt)
        import json
        response_text = response.text.strip()
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
        json_text = json_match.group(1) if json_match else response_text
        data = json.loads(json_text)
        chords = [c["symbol"] for c in data.get("chords", [])]
        analysis = [ChordAnalysis(**c) for c in data.get("chords", [])]
        return chords, data.get("key", key or "E"), data.get("tempo", tempo or 100), analysis

    def _parse_description_fallback(self, description, key, tempo):
        parsed_key = key or "E"
        parsed_tempo = tempo or 100
        # Standard 12-bar blues in E
        chords = ["E7", "E7", "E7", "E7", "A7", "A7", "E7", "E7", "B7", "A7", "E7", "E7"]
        return chords[:12], parsed_key, parsed_tempo

    def _export_to_midi(self, arrangement):
        output_dir = settings.OUTPUTS_DIR / "blues_generated"
        output_dir.mkdir(parents=True, exist_ok=True)
        import time
        filename = f"blues_{arrangement.key}_{arrangement.tempo}bpm_{int(time.time())}.mid"
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

blues_generator_service = BluesGeneratorService()
