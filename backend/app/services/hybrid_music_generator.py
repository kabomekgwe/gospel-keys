"""
Hybrid Music Generator - Orchestrates the complete music generation pipeline.

Combines:
1. musiclang_predict (chord generation)
2. Qwen 2.5-14B (music theory + melody)
3. MidiTok (tokenization)
4. Rust audio engine (synthesis)

This is the main entry point for Phase 1 music generation.
"""

import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any
import mido
import random

from app.services.ai.chord_service import chord_service
from app.services.ai.music_theory_generator import music_theory_generator
from app.services.ai.midi_service import midi_service
from app.services.multi_model_service import multi_model_service
from app.schemas.music_generation import (
    MusicGenerationRequest,
    MusicGenerationResponse,
    ChordProgression,
    MelodySequence,
    MelodyNote,
    ChordVoicing,
    MusicGenre,
    MusicKey,
)

logger = logging.getLogger(__name__)


class HybridMusicGenerator:
    """
    Complete hybrid music generation pipeline.

    Pipeline:
    1. Generate chord progression (musiclang or template)
    2. Generate melody using Qwen 2.5-14B
    3. Combine chords + melody into MIDI
    4. Tokenize MIDI with MidiTok
    5. Synthesize audio with Rust engine

    All processing is 100% local (no API calls).
    """

    def __init__(self):
        self.chord_service = chord_service
        self.theory_generator = music_theory_generator
        self.midi_service = midi_service
        self.llm = multi_model_service

        # Output directories
        self.output_dir = Path("backend/output/hybrid_generation")
        self.midi_dir = self.output_dir / "midi"
        self.audio_dir = self.output_dir / "audio"

        # Create directories
        self.midi_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    async def generate(
        self,
        request: MusicGenerationRequest
    ) -> MusicGenerationResponse:
        """
        Generate complete musical piece from request.

        Args:
            request: Music generation parameters

        Returns:
            Complete response with MIDI, audio, and metadata
        """
        start_time = time.time()
        logger.info(f"🎵 Starting hybrid music generation: {request.genre.value} in {request.key.value}")

        try:
            # Step 1 & 2: Generate/Load Chords and Melody
            if request.template_data:
                logger.info("📄 Using provided template data (World Class Mode)")
                chord_progression, melody = self._parse_template(
                    request.template_data,
                    request.genre,
                    request.key,
                    request.num_bars
                )
                logger.info(f"✓ Loaded {len(chord_progression.chords)} chords and {len(melody.notes)} melody notes from template (extended to {request.num_bars} bars)")
            else:
                # Step 1: Generate chord progression
                logger.info("📝 Step 1: Generating chord progression...")
                chord_progression = await self._generate_chords(request)
                logger.info(f"✓ Generated {len(chord_progression.chords)} chords: {chord_progression.chords}")

                # Step 2: Generate melody (if requested)
                melody = None
                if request.include_melody:
                    logger.info("🎼 Step 2: Generating melody...")
                    melody = await self._generate_melody(request, chord_progression)
                    logger.info(f"✓ Generated {len(melody.notes)} melody notes")
                else:
                    logger.info("⏭️  Step 2: Melody generation skipped")

            # Step 3: Create MIDI file
            logger.info("🎹 Step 3: Creating MIDI file...")
            midi_file = await self._create_midi(request, chord_progression, melody)
            logger.info(f"✓ MIDI file created: {midi_file}")

            # Step 4: Tokenize MIDI
            logger.info("🔢 Step 4: Tokenizing MIDI...")
            midi_tokens = self._tokenize_midi(midi_file)
            logger.info(f"✓ Generated {len(midi_tokens)} tokens")

            # Step 5: Synthesize audio (if requested)
            audio_file = None
            if request.synthesize_audio:
                logger.info("🔊 Step 5: Synthesizing audio...")
                audio_file = await self._synthesize_audio(
                    midi_file,
                    request.use_gpu_synthesis,
                    request.add_reverb
                )
                logger.info(f"✓ Audio synthesized: {audio_file}")
            else:
                logger.info("⏭️  Step 5: Audio synthesis skipped")

            # Step 6: Generate theory analysis (optional)
            theory_analysis = None
            if request.complexity >= 6:
                logger.info("📚 Step 6: Generating theory analysis...")
                theory_analysis = await self._analyze_theory(chord_progression, melody)
                logger.info("✓ Theory analysis complete")

            # Calculate generation time
            generation_time_ms = int((time.time() - start_time) * 1000)
            logger.info(f"✅ Generation complete in {generation_time_ms}ms")

            # Build response
            response = MusicGenerationResponse(
                chord_progression=chord_progression,
                melody=melody,
                midi_file=str(midi_file),
                audio_file=str(audio_file) if audio_file else None,
                midi_tokens=midi_tokens,
                generation_time_ms=generation_time_ms,
                model_info={
                    "chord_model": "musiclang/musiclang-v2",
                    "theory_model": "Qwen2.5-14B-Instruct-4bit (MLX)",
                    "tokenizer": "MidiTok REMI",
                    "synthesizer": "Rust GPU Engine" if request.use_gpu_synthesis else "Rust CPU Engine",
                },
                theory_analysis=theory_analysis,
            )

            return response

        except Exception as e:
            logger.error(f"❌ Hybrid generation failed: {e}", exc_info=True)
            raise e

    async def _generate_chords(
        self,
        request: MusicGenerationRequest
    ) -> ChordProgression:
        """Generate chord progression using musiclang or templates"""
        return await self.chord_service.generate_progression(
            genre=request.genre,
            key=request.key,
            num_bars=request.num_bars,
            style=request.style,
            custom_progression=request.chord_progression,
        )

    async def _generate_melody(
        self,
        request: MusicGenerationRequest,
        chord_progression: ChordProgression
    ) -> Optional[MelodySequence]:
        """Generate melody using Qwen 2.5-14B"""
        # Calculate num_notes based on num_bars (4 notes per bar on average)
        num_notes = request.num_bars * 4

        return await self.theory_generator.generate_melody(
            chord_progression=chord_progression.chords,
            key=request.key,
            genre=request.genre,
            num_notes=num_notes,
            approach="chord_tones",  # Default to chord tones
        )

    async def _create_midi(
        self,
        request: MusicGenerationRequest,
        chord_progression: ChordProgression,
        melody: Optional[MelodySequence]
    ) -> Path:
        """Create MIDI file with realistic piano performance"""
        # Create new MIDI file
        midi_file = mido.MidiFile()
        
        # Track 0: Conductor
        conductor_track = mido.MidiTrack()
        conductor_track.name = "Conductor"
        midi_file.tracks.append(conductor_track)

        # Set tempo
        tempo = mido.bpm2tempo(request.tempo)
        conductor_track.append(mido.MetaMessage('set_tempo', tempo=tempo, time=0))
        conductor_track.append(mido.MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))

        ticks_per_beat = midi_file.ticks_per_beat

        # Track 1: Piano (Combined Hands)
        piano_track = mido.MidiTrack()
        piano_track.name = "Piano"
        midi_file.tracks.append(piano_track)
        piano_track.append(mido.Message('program_change', program=0, time=0)) # Acoustic Grand

        # Combine chords and melody into a single performance
        self._add_piano_performance(piano_track, chord_progression, melody, ticks_per_beat, request.genre)

        # Save MIDI file
        timestamp = int(time.time())
        filename = f"{request.genre.value}_{request.key.value}_{timestamp}.mid"
        midi_path = self.midi_dir / filename

        midi_file.save(midi_path)
        return midi_path

    def _add_piano_performance(
        self,
        track: mido.MidiTrack,
        chords: ChordProgression,
        melody: Optional[MelodySequence],
        ticks_per_beat: int,
        genre: MusicGenre
    ):
        """
        Merge chords and melody into a realistic single-track performance.
        Simulates Left Hand (Bass/Shells) and Right Hand (Melody/Extensions).
        """
        # Collect all note events (on/off) with absolute times in ticks
        events = []
        
        # --- 1. Process Chords (Comping / Harmony) ---
        beats_per_bar = 4
        beats_per_chord = 2 # Assuming 2 chords per bar roughly, or use chord duration if available
        # In our simple model, we assume equal duration chords filling bars.
        # Total bars = chords.num_bars
        # Total beats = total_bars * 4
        # Chords list length.
        total_beats = chords.num_bars * beats_per_bar
        chord_duration_beats = total_beats / len(chords.voicings) if chords.voicings else 2.0
        
        current_beat = 0.0
        
        for voicing in chords.voicings:
            # Analyze Voicing for Hand Split
            # Sort notes
            sorted_notes = sorted(voicing.notes)
            bass_note = sorted_notes[0]
            rest_notes = sorted_notes[1:]
            
            # Left Hand: Bass + Lower Shells
            # Keep LH below C4 (60) usually
            lh_notes = [bass_note]
            rh_comp_notes = []
            
            for n in rest_notes:
                if n < 60:
                    lh_notes.append(n)
                else:
                    rh_comp_notes.append(n)
            
            # Create Note Events
            start_tick = int(current_beat * ticks_per_beat)
            end_tick = int((current_beat + chord_duration_beats) * ticks_per_beat)
             # Slightly shorter for articulation (95%)
            release_tick = start_tick + int((end_tick - start_tick) * 0.95)
            
            # LH Events (Bass - Stronger, Shells - Softer)
            # Humanize Bass: Vel +/- 5, Timing +/- 10 ticks
            bass_vel = (85 if genre == MusicGenre.JAZZ else 80) + random.randint(-5, 5)
            bass_offset = random.randint(0, 10)
            
            events.append({"type": "note_on", "note": bass_note, "vel": min(127, max(1, bass_vel)), "time": start_tick + bass_offset})
            events.append({"type": "note_off", "note": bass_note, "vel": 0, "time": release_tick})
            
            for n in lh_notes[1:]:
                # Humanize Shells
                shell_vel = 65 + random.randint(-8, 8)
                shell_offset = random.randint(5, 20) # Strum effect
                events.append({"type": "note_on", "note": n, "vel": min(127, max(1, shell_vel)), "time": start_tick + shell_offset}) 
                events.append({"type": "note_off", "note": n, "vel": 0, "time": release_tick})

            # RH Comping Events (Softer, maybe rhythmic?)
            # Humanize Comping
            for n in rh_comp_notes:
                comp_vel = 55 + random.randint(-8, 8)
                comp_offset = random.randint(10, 30) # More delay for comping
                events.append({"type": "note_on", "note": n, "vel": min(127, max(1, comp_vel)), "time": start_tick + comp_offset})
                events.append({"type": "note_off", "note": n, "vel": 0, "time": release_tick})
                
            current_beat += chord_duration_beats

        # --- 2. Process Melody (Lead) ---
        if melody:
            for note in melody.notes:
                start_tick = int(note.start_time * ticks_per_beat)
                duration_ticks = int(note.duration * ticks_per_beat)
                end_tick = start_tick + duration_ticks
                
                # Melody usually louder
                base_vel = note.velocity if note.velocity else 95
                human_vel = base_vel + random.randint(-5, 5)
                
                # Micro-timing for melody (lay back or push)
                human_offset = random.randint(-5, 10) 
                
                events.append({"type": "note_on", "note": note.pitch, "vel": min(127, max(1, human_vel)), "time": max(0, start_tick + human_offset)})
                events.append({"type": "note_off", "note": note.pitch, "vel": 0, "time": end_tick})

        # --- 3. Sort and Write Events ---
        # Sort by time, then note_off before note_on if same time (to prevent hanging? actually on before off usually)
        # Standard: Sort by time.
        events.sort(key=lambda x: x["time"])
        
        # Convert absolute time to delta time
        last_time = 0
        for event in events:
            delta = event["time"] - last_time
            # Ensure non-negative (should be if sorted)
            if delta < 0: delta = 0
            
            track.append(mido.Message(
                event["type"],
                note=event["note"],
                velocity=event["vel"],
                time=delta
            ))
            last_time = event["time"]

    def _tokenize_midi(self, midi_file: Path) -> list[int]:
        """Tokenize MIDI file using MidiTok"""
        try:
            tokens = self.midi_service.tokenize_midi_file(str(midi_file))
            return tokens
        except Exception as e:
            logger.error(f"MIDI tokenization failed: {e}")
            return []

    async def _synthesize_audio(
        self,
        midi_file: Path,
        use_gpu: bool,
        add_reverb: bool
    ) -> Optional[Path]:
        """Synthesize audio using Rust engine"""
        try:
            # Import Rust audio engine
            from rust_audio_engine import synthesize_midi

            # Output audio path
            audio_filename = midi_file.stem + ".wav"
            audio_path = self.audio_dir / audio_filename

            # Synthesize (requires soundfont)
            soundfont_path = "backend/soundfonts/piano.sf2"  # Ensure this exists

            duration = synthesize_midi(
                midi_path=str(midi_file),
                output_path=str(audio_path),
                soundfont_path=soundfont_path,
                use_gpu=use_gpu,
                reverb=add_reverb
            )

            logger.info(f"Synthesized {duration:.2f}s of audio")
            return audio_path

        except ImportError:
            logger.warning("Rust audio engine not available. Skipping synthesis.")
            return None
        except Exception as e:
            logger.error(f"Audio synthesis failed: {e}")
            return None

    async def _analyze_theory(
        self,
        chord_progression: ChordProgression,
        melody: Optional[MelodySequence]
    ) -> str:
        """Generate music theory analysis using Qwen 2.5-14B"""
        if not self.llm or not self.llm.is_available():
            return "Theory analysis unavailable (LLM not loaded)"

        try:
            prompt = f"""Analyze this musical piece:

Key: {chord_progression.key.value}
Genre: {chord_progression.genre.value}
Chord progression: {' - '.join(chord_progression.chords)}
Roman numerals: {' - '.join(chord_progression.roman_numerals)}

Provide a brief music theory analysis covering:
1. Key and mode
2. Functional harmony (tonic, subdominant, dominant relationships)
3. Notable harmonic features
4. Genre-specific elements

Keep analysis concise (3-4 sentences)."""

            analysis = self.llm.generate(
                prompt=prompt,
                complexity=6,  # Medium complexity
                max_tokens=256,
                temperature=0.5,
            )

            return analysis.strip()

        except Exception as e:
            logger.error(f"Theory analysis failed: {e}")
            return f"Analysis failed: {str(e)}"

    def _parse_template(
        self,
        template_data: Dict[str, Any],
        genre: MusicGenre,
        key: MusicKey,
        target_bars: int = 8
    ) -> tuple[ChordProgression, MelodySequence]:
        """Parse full music template into ChordProgression and MelodySequence"""
        
        raw_measures = template_data.get('measures', [])
        measures = []
        
        # Loop measures to fill target_bars
        if raw_measures:
            while len(measures) < target_bars:
                for m in raw_measures:
                    if len(measures) < target_bars:
                        measures.append(m)
                    else:
                        break
        
        chords_list = []
        voicings_list = []
        melody_notes = []
        
        # Duration mapping (assuming 4/4)
        duration_map = {
            "whole": 4.0,
            "half": 2.0,
            "dotted quarter": 1.5,
            "quarter": 1.0,
            "dotted eighth": 0.75,
            "eighth": 0.5,
            "triplet": 0.33,
            "sixteenth": 0.25,
            "thirty-second": 0.125
        }

        # Note mapping helper
        note_name_map = {
            "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
            "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
            "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
        }
        
        def parse_note(note_str: str) -> int:
            if note_str == "rest": return -1
            # Handle "D4", "F#3", "Bb5"
            try:
                pitch_class = ""
                octave_part = ""
                if len(note_str) == 3: # e.g. F#4
                    pitch_class = note_str[:2]
                    octave_part = note_str[2:]
                else: # e.g. C4
                    pitch_class = note_str[:1]
                    octave_part = note_str[1:]
                
                octave = int(octave_part)
                # MIDI note C4 is 60. Octave 4 * 12 + C(0) = 48? No.
                # Standard: C4 = 60.
                # note_name_map["C"] is 0.
                # (Octave + 1) * 12 + note_name_map.
                # (4 + 1) * 12 = 60. Correct.
                midi = (octave + 1) * 12 + note_name_map.get(pitch_class, 0)
                return midi
            except:
                return 60 # Default C4

        total_bars = len(measures)
        current_beat_global = 0.0
        
        for measure in measures:
            # Assumes sequential measures
            
            # --- Parse Chords ---
            m_chords = measure.get('chords', [])
            # Usually chords are at start of measure or specific beats
            # For simplicity, we assume one chord per measure or process all
            for chord_data in m_chords:
                symbol = chord_data.get('symbol', 'C')
                # Determine basic root from symbol
                root_str = symbol
                if len(symbol) > 1 and symbol[1] in ['#', 'b']:
                    root_str = symbol[:2]
                else:
                    root_str = symbol[:1]
                
                # Default root octave 3 (48-59) or 4 (60-71)
                root_val = note_name_map.get(root_str, 0)
                root_midi = (4 * 12) + root_val 
                
                # Generate voicing using chord service logic (reusing existing logic for now)
                # We need a list of notes. 
                # Accessing private method for now, or duplicate logic
                notes = self.chord_service._get_chord_notes(symbol, root_midi, genre)
                bass_note = notes[0] - 12 if notes else root_midi - 12
                
                voicing = ChordVoicing(
                    chord_symbol=symbol,
                    root=root_midi,
                    notes=notes,
                    inversion=0,
                    bass_note=bass_note
                )
                
                chords_list.append(symbol)
                voicings_list.append(voicing)
            
            # --- Parse Melody ---
            m_melody = measure.get('melody', [])
            current_measure_beat = 0.0
            
            for m_note in m_melody:
                note_str = m_note.get('note', 'rest')
                dur_str = m_note.get('duration', 'quarter')
                duration = duration_map.get(dur_str, 1.0)
                
                if note_str != 'rest':
                    midi_pitch = parse_note(note_str)
                    # Absolute beat time
                    start_time = current_beat_global + current_measure_beat
                    
                    melody_note = MelodyNote(
                        pitch=midi_pitch,
                        start_time=start_time,
                        duration=duration,
                        velocity=90 + (10 if m_note.get('articulation') == 'accent' else 0)
                    )
                    melody_notes.append(melody_note)
                
                current_measure_beat += duration
            
            current_beat_global += 4.0 # Assume 4/4 per measure

        # Construct MelodySequence
        # Determine range
        pitches = [n.pitch for n in melody_notes]
        range_low = min(pitches) if pitches else 60
        range_high = max(pitches) if pitches else 72
        
        melody_sequence = MelodySequence(
            notes=melody_notes,
            key=key,
            scale="chromatic", # Template derived
            range_low=range_low,
            range_high=range_high,
            approach="template"
        )
        
        # Construct ChordProgression
        # Roman numerals - placeholder
        roman_numerals = ["?"] * len(chords_list)
        
        chord_progression = ChordProgression(
            chords=chords_list,
            roman_numerals=roman_numerals,
            voicings=voicings_list,
            key=key,
            genre=genre,
            num_bars=total_bars,
            time_signature="4/4"
        )
        
        return chord_progression, melody_sequence


# Global singleton instance
hybrid_music_generator = HybridMusicGenerator()
