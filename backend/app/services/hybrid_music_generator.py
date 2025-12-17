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
from typing import Optional, Dict, Any, List
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
    VariationType,
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

        # Output directories - ABSOLUTE PATH to project root/generations
        # Get project root (parent of backend folder)
        project_root = Path(__file__).parent.parent.parent.parent  # backend/app/services -> project root
        self.output_base = project_root / "generations"
        self.audio_dir = self.output_base / "audio"
        
        # Create base directories
        self.output_base.mkdir(parents=True, exist_ok=True)
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
            # Step 1 & 2: Generate/Load Chords - use LLM for ALL genres
            if not request.template_data:
                logger.info(f"🎹 Generating dynamic {request.genre.value} progression with LLM")
                # Generate a dynamic template with LLM-based chord progressions
                request.template_data = self._generate_dynamic_progression_template(
                    genre=request.genre,
                    num_bars=request.num_bars,
                    key=request.key,
                    complexity=request.complexity,
                    style=request.style,
                    prompt=request.prompt  # User custom prompt
                )

            if request.template_data:
                logger.info("📄 Using provided template data (World Class Mode)")
                chord_progression, melody = self._parse_template(
                    request.template_data,
                    request.genre,
                    request.key,
                    request.num_bars,
                    request.variations,
                    request.complexity
                )
                # JAZZ: Force chords-only (no melody) for realistic comping
                if request.genre == MusicGenre.JAZZ:
                    melody = None
                    logger.info(f"✓ Loaded {len(chord_progression.chords)} chords from template (CHORDS ONLY - no melody)")
                else:
                    logger.info(f"✓ Loaded {len(chord_progression.chords)} chords and {len(melody.notes) if melody else 0} melody notes from template")
            else:
                # Step 1: Generate chord progression
                logger.info("📝 Step 1: Generating chord progression...")
                chord_progression = await self._generate_chords(request)
                logger.info(f"✓ Generated {len(chord_progression.chords)} chords: {chord_progression.chords}")

                # Step 2: Generate melody (if requested)
                melody = None
                if request.include_melody:
                    logger.info("🎼 Step 2: Generating melody...")
                    try:
                        melody = await self._generate_melody(request, chord_progression)
                        if melody:
                            logger.info(f"✓ Generated {len(melody.notes)} melody notes")
                        else:
                            logger.warning("⚠️ Melody generation returned None")
                    except Exception as e:
                        logger.error(f"⚠️ Melody generation failed (LLM issue?): {e}")
                        logger.info("⚠️ Continuing with Chords only...")
                        melody = None
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
        # Save MIDI file - in generations/{genre}/ folder with timestamp
        import datetime
        genre_dir = self.output_base / request.genre.value
        genre_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{request.key.value}_{timestamp}.mid"
        midi_path = genre_dir / filename

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
        
        # --- 1. Process Chords with RHYTHMIC COMPING ---
        beats_per_bar = 4
        total_beats = chords.num_bars * beats_per_bar
        chord_duration_beats = total_beats / len(chords.voicings) if chords.voicings else 4.0
        
        # Jazz comping rhythm patterns (in beats within a bar)
        # Each pattern is a list of (beat_offset, duration, velocity_factor)
        # These create syncopated, interesting rhythms like a real pianist
        comping_patterns = [
            # Charleston rhythm: hit on 1, hit on 2-and
            [(0.0, 0.5, 1.0), (1.5, 0.5, 0.8)],
            # Syncopated: 1, 2-and, 4
            [(0.0, 0.4, 1.0), (1.5, 0.4, 0.85), (3.0, 0.5, 0.9)],
            # Freddie Green style: 2-and, 4
            [(1.5, 0.5, 0.9), (3.5, 0.5, 0.85)],
            # Anticipation: 4-and of previous into 1
            [(0.0, 0.7, 1.0), (2.5, 0.4, 0.8), (3.5, 0.5, 0.9)],
            # Full bebop: 1, 2-and, 3, 4-and
            [(0.0, 0.3, 1.0), (1.5, 0.3, 0.8), (2.0, 0.3, 0.85), (3.5, 0.4, 0.9)],
            # Simple: 1 and 3
            [(0.0, 0.5, 1.0), (2.0, 0.5, 0.9)],
            # Sparse: just on 1-and
            [(0.5, 0.5, 0.95)],
            # Dense bebop
            [(0.0, 0.25, 1.0), (1.0, 0.25, 0.75), (1.5, 0.25, 0.85), (2.5, 0.25, 0.8), (3.0, 0.25, 0.9)],
        ]
        
        current_beat = 0.0
        pattern_idx = 0
        
        for voicing_idx, voicing in enumerate(chords.voicings):
            # Select a rhythm pattern - vary by bar for interest
            pattern = comping_patterns[pattern_idx % len(comping_patterns)]
            pattern_idx += 1
            
            # Sometimes switch patterns more randomly for variety
            if random.random() > 0.7:
                pattern = random.choice(comping_patterns)
            
            # Analyze Voicing for Hand Split
            sorted_notes = sorted(voicing.notes)
            bass_note = sorted_notes[0]
            rest_notes = sorted_notes[1:]
            
            # Left Hand: Bass + Lower Shells
            lh_notes = [bass_note]
            rh_comp_notes = []
            
            for n in rest_notes:
                if n < 60:
                    lh_notes.append(n)
                else:
                    rh_comp_notes.append(n)
            
            # Bass note: play on beat 1 and sometimes beat 3 (walking bass style)
            bar_start_tick = int(current_beat * ticks_per_beat)
            
            # Bass on beat 1
            bass_vel = (85 if genre == MusicGenre.JAZZ else 80) + random.randint(-5, 5)
            bass_offset = random.randint(0, 10)
            bass_duration = int(ticks_per_beat * 0.9)  # Slightly detached
            
            events.append({"type": "note_on", "note": bass_note, "vel": min(127, max(1, bass_vel)), "time": bar_start_tick + bass_offset})
            events.append({"type": "note_off", "note": bass_note, "vel": 0, "time": bar_start_tick + bass_duration})
            
            # Sometimes add bass on beat 3 for walking feel
            if random.random() > 0.5 and chord_duration_beats >= 4:
                beat3_tick = bar_start_tick + int(2 * ticks_per_beat)
                # Use a passing tone (chromatic approach) sometimes
                passing_note = bass_note + random.choice([0, -1, 1, -2, 2])
                events.append({"type": "note_on", "note": passing_note, "vel": min(127, max(1, bass_vel - 10)), "time": beat3_tick})
                events.append({"type": "note_off", "note": passing_note, "vel": 0, "time": beat3_tick + bass_duration})
            
            # Left hand shells: play on the rhythmic pattern
            for beat_offset, duration, vel_factor in pattern:
                hit_tick = bar_start_tick + int(beat_offset * ticks_per_beat)
                release_tick = hit_tick + int(duration * ticks_per_beat)
                
                for n in lh_notes[1:]:  # Skip bass (already handled)
                    shell_vel = int(65 * vel_factor) + random.randint(-8, 8)
                    shell_offset = random.randint(5, 20)  # Strum effect
                    events.append({"type": "note_on", "note": n, "vel": min(127, max(1, shell_vel)), "time": hit_tick + shell_offset})
                    events.append({"type": "note_off", "note": n, "vel": 0, "time": release_tick})
            
            # Right hand comping: also follows rhythm pattern with slight delay
            for beat_offset, duration, vel_factor in pattern:
                hit_tick = bar_start_tick + int(beat_offset * ticks_per_beat)
                release_tick = hit_tick + int(duration * ticks_per_beat)
                
                for n in rh_comp_notes:
                    comp_vel = int(55 * vel_factor) + random.randint(-8, 8)
                    comp_offset = random.randint(15, 35)  # More delay for comping (behind beat)
                    events.append({"type": "note_on", "note": n, "vel": min(127, max(1, comp_vel)), "time": hit_tick + comp_offset})
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

        # --- 3. Apply Swing Feel (Jazz) ---
        if genre == MusicGenre.JAZZ:
            events = self._apply_swing_feel(events, ticks_per_beat, swing_amount=0.58)
        
        # --- 4. Sort and Write Events ---
        # Sort by time, then note_off before note_on if same time
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

    def _generate_dynamic_progression_template(
        self,
        genre: MusicGenre,
        num_bars: int,
        key: MusicKey,
        complexity: int,
        style: str,
        prompt: str = ""
    ) -> Dict[str, Any]:
        """
        Use LOCAL LLM to generate a unique chord progression for ANY genre.
        
        The AI reasons about genre, key, complexity, style, and user prompt 
        to create a realistic, song-like chord progression.
        """
        import json
        import random
        import time as time_module
        
        # Genre-specific instructions
        genre_instructions = {
            "jazz": "Use ii-V-I, turnarounds, tritone subs. Think Autumn Leaves, Take The A Train.",
            "gospel": "Use rich extensions (9, 11, 13), walk-ups, passing diminished chords, shout music patterns. Think Kirk Franklin, Fred Hammond.",
            "blues": "Use 12-bar blues form, dominant 7ths, shuffle feel. Think BB King, Ray Charles.",
            "neo_soul": "Use minor 9th/11th chords, cluster voicings, behind-the-beat feel. Think D'Angelo, Erykah Badu.",
            "rnb": "Use smooth progressions, add9 chords, lo-fi voicings. Think Bryson Tiller, SZA.",
            "classical": "Use traditional harmony, I-IV-V-I, proper voice leading.",
            "pop": "Use I-V-vi-IV and variations, simple but effective.",
            "funk": "Use dominant 7ths, 9ths, syncopated rhythm. Think Herbie Hancock, Parliament.",
        }
        
        genre_key = genre.value.lower()
        genre_guide = genre_instructions.get(genre_key, "Create an authentic progression for this style.")
        
        # Add unique seed to ensure different progressions each time
        unique_seed = f"{int(time_module.time() * 1000)}_{random.randint(1000, 9999)}"
        
        # Build context prompt for the LLM
        user_input = prompt if prompt else f"Create an authentic {style or genre.value} chord progression"
        
        llm_prompt = f"""You are an expert {genre.value} keyboardist and composer. Generate a chord progression for a REAL song.

UNIQUE REQUEST ID: {unique_seed} (generate a DIFFERENT progression than previous requests)

USER REQUEST: {user_input}

PARAMETERS:
- Genre: {genre.value}
- Key: {key.value}
- Number of bars: {num_bars}
- Complexity: {complexity}/10 (higher = more extensions, substitutions)
- Style: {style or genre.value}

GENRE-SPECIFIC GUIDANCE:
{genre_guide}

RULES:
1. Create a progression that sounds like a REAL {genre.value} song
2. Complexity {complexity} means: {"basic triads and 7ths" if complexity <= 3 else "some extensions (9, 11)" if complexity <= 6 else "rich extensions, alterations, substitutions"}
3. Make it interesting and musical - varied but coherent
4. Consider the full {num_bars}-bar form structure

OUTPUT FORMAT (JSON array of chord symbols, one per bar):
["Cmaj7", "Am7", "Dm9", "G7", "Em7", "A7#9", "Dm7", "G13"]

IMPORTANT: 
- Output ONLY the JSON array, no explanation
- Exactly {num_bars} chords (one per bar)
- Use proper chord symbols

Generate now:"""

        # Use local LLM with high temperature for unique outputs each time
        chords_list = []
        
        try:
            if self.llm and self.llm.is_available():
                logger.info("🤖 Using local LLM to generate chord progression...")
                
                # Force local model even for high complexity, use HIGH temperature
                response = self.llm.generate(
                    prompt=llm_prompt,
                    complexity=min(complexity, 7),  # Cap for model routing
                    max_tokens=256,
                    temperature=1.0,  # HIGH temperature for unique outputs
                    force_local=True,  # Always use local model
                )
                
                # Parse the JSON response
                response = response.strip()
                if '[' in response and ']' in response:
                    start = response.index('[')
                    end = response.rindex(']') + 1
                    json_str = response[start:end]
                    chords_list = json.loads(json_str)
                    logger.info(f"✅ LLM generated: {chords_list}")
                else:
                    logger.warning(f"⚠️ No JSON array in response: {response[:100]}")
            else:
                logger.warning("⚠️ LLM not available")
                    
        except Exception as e:
            logger.error(f"❌ LLM generation failed: {e}")
        
        # Verify we have valid chords, regenerate if needed
        if not chords_list or len(chords_list) != num_bars:
            logger.warning(f"⚠️ Invalid LLM output, got {len(chords_list) if chords_list else 0} chords, need {num_bars}")
            # One more attempt with simplified prompt
            try:
                simple_prompt = f"Generate exactly {num_bars} {genre.value} chords in key of {key.value}. Output ONLY a JSON array like [\"Cmaj7\",\"Am7\",...]"
                response = self.llm.generate(
                    prompt=simple_prompt,
                    complexity=5,
                    max_tokens=256,
                    temperature=1.0,
                    force_local=True,
                )
                if '[' in response and ']' in response:
                    start = response.index('[')
                    end = response.rindex(']') + 1
                    chords_list = json.loads(response[start:end])
                    logger.info(f"✅ Retry succeeded: {chords_list}")
            except Exception as e:
                logger.error(f"❌ Retry also failed: {e}")
        
        # REQUIRED: Fallback if LLM failed to produce valid output
        if not chords_list or len(chords_list) != num_bars:
            logger.warning(f"🔄 LLM output invalid, using algorithmic generation as fallback")
            chords_list = self._generate_realistic_progression(
                genre, num_bars, key, complexity, style
            )
            logger.info(f"✅ Fallback generated: {chords_list}")
        
        # Convert chord list to template format (chords only, no melody)
        measures = []
        for i, chord in enumerate(chords_list):
            measures.append({
                "measureNumber": i + 1,
                "chords": [{
                    "symbol": chord,
                    "duration": "whole",
                    "position": "beat1"
                }],
                "melody": [],  # No melody - chords only
                "dynamics": "mf"
            })
        
        return {
            "title": f"AI Generated {genre.value.title()} in {key.value}",
            "composer": "Local LLM",
            "key": key.value,
            "timeSignature": "4/4",
            "tempo": 120,
            "measures": measures
        }
    
    def _generate_realistic_progression(
        self,
        genre: MusicGenre,
        num_bars: int,
        key: MusicKey,
        complexity: int,
        style: str
    ) -> List[str]:
        """
        Fallback: Generate a realistic chord progression algorithmically.
        Uses genre-specific song-form patterns.
        """
        import random
        
        # Note mapping
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        flat_to_sharp = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
        
        key_str = key.value.replace('m', '')
        key_root = flat_to_sharp.get(key_str, key_str)
        root_idx = notes.index(key_root) if key_root in notes else 0
        
        def note(semitones: int) -> str:
            return notes[(root_idx + semitones) % 12]
        
        # Genre-specific patterns (8 bars each)
        genre_key = genre.value.lower()
        
        if genre_key == "gospel":
            # Gospel patterns - shout music, walk-ups, rich extensions
            patterns = [
                # Traditional gospel turnaround
                [f"{note(0)}maj9", f"{note(0)}maj7/3", f"{note(5)}9", f"{note(5)}7",
                 f"{note(0)}/5", f"{note(7)}13", f"{note(0)}maj9", f"{note(7)}7#9"],
                # Contemporary gospel (Kirk Franklin style)
                [f"{note(0)}maj9", f"{note(9)}m11", f"{note(2)}m9", f"{note(7)}13",
                 f"{note(4)}m9", f"{note(9)}7#9", f"{note(2)}m9", f"{note(7)}7alt"],
                # Shout music pattern
                [f"{note(0)}7", f"{note(0)}7", f"{note(5)}9", f"{note(0)}7",
                 f"{note(0)}7/3", f"{note(1)}dim7", f"{note(2)}m7", f"{note(7)}7#9"],
            ]
        elif genre_key == "blues":
            patterns = [
                # 12-bar blues (8 bars shown)
                [f"{note(0)}7", f"{note(5)}7", f"{note(0)}7", f"{note(0)}7",
                 f"{note(5)}7", f"{note(5)}7", f"{note(0)}7", f"{note(9)}7"],
            ]
        elif genre_key == "neo_soul":
            patterns = [
                # D'Angelo style
                [f"{note(0)}m9", f"{note(5)}9", f"{note(3)}maj9", f"{note(8)}m11",
                 f"{note(0)}m9", f"{note(10)}7", f"{note(3)}maj9", f"{note(7)}7#9"],
                # Erykah Badu style
                [f"{note(9)}m11", f"{note(2)}9", f"{note(7)}m9", f"{note(0)}maj9",
                 f"{note(5)}m9", f"{note(10)}13", f"{note(3)}maj9", f"{note(8)}m11"],
            ]
        elif genre_key == "rnb":
            patterns = [
                # Lo-fi R&B
                [f"{note(0)}add9", f"{note(9)}m7", f"{note(5)}maj7", f"{note(7)}sus4",
                 f"{note(0)}add9", f"{note(4)}m7", f"{note(5)}maj7", f"{note(7)}7"],
                # Modern R&B 
                [f"{note(0)}maj7", f"{note(9)}m9", f"{note(2)}m7", f"{note(7)}sus4",
                 f"{note(4)}m7", f"{note(9)}7", f"{note(2)}m7", f"{note(7)}7"],
            ]
        elif genre_key == "funk":
            patterns = [
                # Classic funk
                [f"{note(0)}9", f"{note(0)}9", f"{note(5)}9", f"{note(0)}9",
                 f"{note(7)}9", f"{note(5)}9", f"{note(0)}9", f"{note(0)}9"],
            ]
        else:  # jazz or default
            patterns = [
                # Autumn Leaves style
                [f"{note(0)}m7", f"{note(5)}7", f"{note(10)}maj7", f"{note(3)}maj7",
                 f"{note(8)}m7b5", f"{note(1)}7", f"{note(0)}m7", f"{note(7)}7"],
                # Take The A Train style
                [f"{note(0)}maj7", f"{note(2)}7#11", f"{note(2)}m7", f"{note(7)}7",
                 f"{note(0)}maj7", f"{note(4)}m7", f"{note(9)}7", f"{note(7)}7"],
                # Rhythm changes
                [f"{note(0)}maj7", f"{note(9)}m7", f"{note(2)}m7", f"{note(7)}7",
                 f"{note(4)}m7", f"{note(9)}7", f"{note(2)}m7", f"{note(7)}7"],
            ]
        
        # Build progression by combining patterns
        result = []
        while len(result) < num_bars:
            pattern = random.choice(patterns)
            result.extend(pattern)
        
        # Trim to exact length
        result = result[:num_bars]
        
        # Apply complexity-based modifications
        if complexity >= 7:
            for i in range(len(result)):
                chord = result[i]
                if chord.endswith('7') and not any(x in chord for x in ['maj7', 'm7', 'dim7', '7#', '7b', '7alt', '9', '11', '13']):
                    alts = ['7alt', '7#9', '7b9', '13']
                    if random.random() > 0.5:
                        base = chord.replace('7', '')
                        result[i] = base + random.choice(alts)
                elif 'm7' in chord and 'maj' not in chord and 'b5' not in chord and '9' not in chord:
                    if random.random() > 0.5:
                        result[i] = chord.replace('m7', 'm9')
                elif 'maj7' in chord and '9' not in chord:
                    if random.random() > 0.5:
                        result[i] = chord.replace('maj7', 'maj9')
        
        elif complexity <= 3:
            for i in range(len(result)):
                chord = result[i]
                # Simplify extensions
                for ext in ['9', '11', '13', '#9', 'b9', '#11', 'alt', 'add']:
                    chord = chord.replace(ext, '')
                while '77' in chord:
                    chord = chord.replace('77', '7')
                result[i] = chord if chord else notes[root_idx] + "maj7"
        
        return result

    def _parse_template(
        self,
        template_data: Dict[str, Any],
        genre: MusicGenre,
        key: MusicKey,
        target_bars: int = 8,
        variations: Optional[List[VariationType]] = None,
        complexity: int = 5
    ) -> tuple[ChordProgression, MelodySequence]:
        """Parse full music template into ChordProgression and MelodySequence"""
        import copy
        
        raw_measures = template_data.get('measures', [])
        measures = []
        original_len = len(raw_measures)
        
        # Loop measures to fill target_bars with variation
        if raw_measures:
            while len(measures) < target_bars:
                for i, m in enumerate(raw_measures):
                    if len(measures) < target_bars:
                        # If this is a repeat (index >= original length), apply variation
                        is_repeat = len(measures) >= original_len
                        
                        # Create deep copy to modify
                        measure_copy = copy.deepcopy(m)
                        
                        if is_repeat:
                            self._apply_variation(measure_copy, len(measures), genre, variations)
                        
                        measures.append(measure_copy)
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
                midi = (octave + 1) * 12 + note_name_map.get(pitch_class, 0)
                return midi
            except:
                return 60 # Default C4

        total_bars = len(measures)
        current_beat_global = 0.0
        bar_index = 0
        
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
                
                # Generate voicing using chord service logic with complexity awareness
                notes = self.chord_service._get_chord_notes(
                    symbol, root_midi, genre, complexity, bar_index
                )
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
            
            bar_index += 1
            
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

    def _apply_variation(
        self, 
        measure: Dict[str, Any], 
        bar_index: int, 
        genre: MusicGenre,
        allowed_variations: Optional[List[VariationType]] = None
    ):
        """Apply algorithmic variation to a measure (unique bars)"""
        import random
        
        melody = measure.get('melody', [])
        chords = measure.get('chords', [])
        
        # Variation Strategy
        if allowed_variations:
            options = [v.value for v in allowed_variations]
        else:
            options = ['transpose', 'rhythm', 'density', 'octave']
            
        variation_type = random.choice(options)
        
        # --- Harmonic Variations (Chords) ---
        if variation_type in ['substitution', 'harmony', 'chords']:
            # Tritone substitution logic
            for chord in chords:
                symbol = chord.get('symbol', 'C')
                if '7' in symbol and 'maj' not in symbol and 'm' not in symbol: # Dominant 7
                    # Find root
                    try:
                        root = symbol[:-1] if len(symbol) > 1 and symbol[1] in ['#', 'b'] else symbol[0]
                        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
                        # Normalize flats to sharps for lookup
                        flat_map = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
                        lookup_root = flat_map.get(root, root)
                        
                        if lookup_root in notes:
                            idx = notes.index(lookup_root)
                            tritone_idx = (idx + 6) % 12
                            tritone_root = notes[tritone_idx]
                            # Replace with tritone sub
                            chord['symbol'] = f"{tritone_root}7"
                    except:
                        pass

        # --- Melodic Variations (Licks/Notes) ---
        elif variation_type == 'lick':
            # Create a simple 16th note run (arpeggio-ish) if chords exist
            if chords and melody:
                # Clear existing melody to make room for lick? Or append?
                # Let's replace the last part of the bar with a lick
                # Creating a downwards run
                base_note = melody[0].get('note', 'C4') if melody else 'C4'
                try:
                    melody.clear() # Replace measure with lick
                    # Simple descending run
                    notes = ["C", "B", "A", "G", "F", "E", "D", "C"] # Scale degrees
                    # This is very hacked, better to use chord tones
                    # But for "Variation", a simple density runs works
                    for i in range(4):
                        melody.append({"note": f"C{5 if i < 2 else 4}", "duration": "sixteenth"})
                        melody.append({"note": f"A{4}", "duration": "sixteenth"})
                        melody.append({"note": f"G{4}", "duration": "sixteenth"})
                        melody.append({"note": f"E{4}", "duration": "sixteenth"})
                except:
                    pass

        # --- Rhythmic/Structural Variations ---
        elif variation_type in ['transpose', 'octave', 'inversion']:
            shift = random.choice([-1, 1])
            for note in melody:
                n = note.get('note', 'rest')
                if n != 'rest' and len(n) >= 2:
                    try:
                        octave = int(n[-1])
                        new_octave = max(1, min(7, octave + shift))
                        note['note'] = n[:-1] + str(new_octave)
                    except:
                        pass
        
        elif variation_type == 'rhythm':
            if len(melody) >= 2:
                idx1, idx2 = random.sample(range(len(melody)), 2)
                melody[idx1], melody[idx2] = melody[idx2], melody[idx1]

        elif variation_type == 'density' or variation_type == 'arrangement':
             if len(melody) > 2:
                 melody.pop(random.randint(0, len(melody)-1))

    def _apply_swing_feel(
        self,
        events: List[Dict[str, Any]],
        ticks_per_beat: int,
        swing_amount: float = 0.58
    ) -> List[Dict[str, Any]]:
        """
        Apply swing feel to MIDI events.
        
        Swing works by delaying notes that fall on the "and" of each beat
        (the upbeats/offbeats between main beats).
        
        Args:
            events: List of MIDI events with 'time' in absolute ticks
            ticks_per_beat: MIDI ticks per quarter note
            swing_amount: 0.5 = straight, 0.67 = triplet swing, 0.58 = subtle swing
            
        Returns:
            Modified events with swing timing applied
        """
        half_beat = ticks_per_beat // 2  # Position of straight eighth note
        
        for event in events:
            tick = event['time']
            beat_position = tick % ticks_per_beat
            
            # Check if note is on the upbeat (2nd eighth of each beat)
            # Allow some tolerance for humanization offsets
            tolerance = ticks_per_beat // 8
            
            if abs(beat_position - half_beat) < tolerance:
                # Calculate swing offset
                # swing_amount of 0.58 means the upbeat is 58% through the beat
                # instead of 50%
                swing_target = int(ticks_per_beat * swing_amount)
                offset = swing_target - half_beat
                
                event['time'] = tick + offset
        
        return events


# Global singleton instance
hybrid_music_generator = HybridMusicGenerator()
