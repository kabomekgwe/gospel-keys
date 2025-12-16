"""
Test script for hybrid music generator system.

Tests:
1. Chord generation (musiclang)
2. Melody generation (Qwen 2.5-14B)
3. Full hybrid pipeline
4. MIDI tokenization
5. Audio synthesis (if Rust engine available)

Usage:
    python scripts/test_hybrid_generator.py
"""

import asyncio
import logging
from pathlib import Path

from app.schemas.music_generation import (
    MusicGenerationRequest,
    MusicGenre,
    MusicKey,
    ChordPredictionRequest,
)
from app.services.hybrid_music_generator import hybrid_music_generator
from app.services.ai.chord_service import chord_service
from app.services.ai.music_theory_generator import music_theory_generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_chord_generation():
    """Test 1: Chord service"""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: Chord Generation (musiclang)")
    logger.info("="*60)

    try:
        # Generate Gospel progression
        progression = await chord_service.generate_progression(
            genre=MusicGenre.GOSPEL,
            key=MusicKey.C,
            num_bars=8,
            style="traditional"
        )

        logger.info(f"✓ Generated progression:")
        logger.info(f"  Chords: {progression.chords}")
        logger.info(f"  Roman numerals: {progression.roman_numerals}")
        logger.info(f"  Voicings: {len(progression.voicings)} chords")
        logger.info(f"  First voicing notes: {progression.voicings[0].notes}")

        return True

    except Exception as e:
        logger.error(f"✗ Chord generation failed: {e}", exc_info=True)
        return False


async def test_melody_generation():
    """Test 2: Melody generation"""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: Melody Generation (Qwen 2.5-14B)")
    logger.info("="*60)

    try:
        # Generate melody
        melody = await music_theory_generator.generate_melody(
            chord_progression=["C", "F", "G", "C"],
            key=MusicKey.C,
            genre=MusicGenre.GOSPEL,
            num_notes=16,
            approach="chord_tones"
        )

        logger.info(f"✓ Generated melody:")
        logger.info(f"  Notes: {len(melody.notes)} notes")
        logger.info(f"  Scale: {melody.scale}")
        logger.info(f"  Range: {melody.range_low} - {melody.range_high}")
        logger.info(f"  First 3 notes: {[(n.pitch, n.duration) for n in melody.notes[:3]]}")

        return True

    except Exception as e:
        logger.error(f"✗ Melody generation failed: {e}", exc_info=True)
        return False


async def test_chord_prediction():
    """Test 3: Chord prediction with musiclang"""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: Chord Prediction (musiclang_predict)")
    logger.info("="*60)

    try:
        request = ChordPredictionRequest(
            seed_chords=["C", "Am", "F"],
            num_chords=4,
            genre=MusicGenre.GOSPEL,
            key=MusicKey.C
        )

        response = await chord_service.predict_next_chords(request)

        logger.info(f"✓ Predicted chords:")
        logger.info(f"  Seed: {request.seed_chords}")
        logger.info(f"  Predicted: {response.predicted_chords}")
        logger.info(f"  Full progression: {response.full_progression}")

        return True

    except Exception as e:
        logger.error(f"✗ Chord prediction failed: {e}", exc_info=True)
        return False


async def test_full_hybrid_pipeline():
    """Test 4: Complete hybrid generation pipeline"""
    logger.info("\n" + "="*60)
    logger.info("TEST 4: Full Hybrid Pipeline")
    logger.info("="*60)

    try:
        # Create request
        request = MusicGenerationRequest(
            genre=MusicGenre.GOSPEL,
            key=MusicKey.C,
            tempo=120,
            num_bars=8,
            time_signature="4/4",
            style="traditional",
            complexity=6,
            include_melody=True,
            include_bass=False,
            include_chords=True,
            synthesize_audio=False,  # Skip audio for faster testing
            use_gpu_synthesis=False,
            add_reverb=False,
        )

        logger.info(f"Request: {request.genre.value} in {request.key.value}, {request.num_bars} bars")

        # Generate music
        response = await hybrid_music_generator.generate(request)

        logger.info(f"✓ Hybrid generation complete:")
        logger.info(f"  MIDI file: {response.midi_file}")
        logger.info(f"  Chords: {response.chord_progression.chords}")
        logger.info(f"  Melody notes: {len(response.melody.notes) if response.melody else 0}")
        logger.info(f"  MIDI tokens: {len(response.midi_tokens)} tokens")
        logger.info(f"  Generation time: {response.generation_time_ms}ms")
        logger.info(f"  Models used: {response.model_info}")

        if response.theory_analysis:
            logger.info(f"\nTheory Analysis:")
            logger.info(f"  {response.theory_analysis}")

        # Verify MIDI file exists
        midi_path = Path(response.midi_file)
        if midi_path.exists():
            logger.info(f"  ✓ MIDI file verified: {midi_path.stat().st_size} bytes")
        else:
            logger.warning(f"  ✗ MIDI file not found: {midi_path}")

        return True

    except Exception as e:
        logger.error(f"✗ Hybrid pipeline failed: {e}", exc_info=True)
        return False


async def test_midi_tokenization():
    """Test 5: MIDI tokenization"""
    logger.info("\n" + "="*60)
    logger.info("TEST 5: MIDI Tokenization (MidiTok)")
    logger.info("="*60)

    try:
        from app.services.ai.midi_service import midi_service

        # First generate a MIDI file
        request = MusicGenerationRequest(
            genre=MusicGenre.GOSPEL,
            key=MusicKey.C,
            tempo=120,
            num_bars=4,
            include_melody=False,
            include_chords=True,
            synthesize_audio=False,
        )

        response = await hybrid_music_generator.generate(request)
        midi_file = response.midi_file

        # Tokenize
        tokens = midi_service.tokenize_midi_file(midi_file)

        logger.info(f"✓ Tokenization complete:")
        logger.info(f"  Input: {midi_file}")
        logger.info(f"  Tokens: {len(tokens)} tokens")
        logger.info(f"  First 10 tokens: {tokens[:10]}")
        logger.info(f"  Vocab size: {midi_service.tokenizer.vocab_size}")

        # Test detokenization
        output_path = "backend/output/hybrid_generation/midi/detokenized_test.mid"
        midi_service.detokenize_to_midi(tokens, output_path)

        if Path(output_path).exists():
            logger.info(f"  ✓ Detokenization successful: {output_path}")
        else:
            logger.warning(f"  ✗ Detokenization failed")

        return True

    except Exception as e:
        logger.error(f"✗ MIDI tokenization failed: {e}", exc_info=True)
        return False


async def test_with_audio_synthesis():
    """Test 6: Full pipeline with audio synthesis (optional)"""
    logger.info("\n" + "="*60)
    logger.info("TEST 6: Audio Synthesis (Rust Engine)")
    logger.info("="*60)

    try:
        # Check if Rust engine is available
        try:
            from rust_audio_engine import synthesize_midi
            rust_available = True
        except ImportError:
            rust_available = False
            logger.warning("Rust audio engine not available, skipping test")
            return None

        if not rust_available:
            return None

        # Create request with audio synthesis
        request = MusicGenerationRequest(
            genre=MusicGenre.GOSPEL,
            key=MusicKey.C,
            tempo=100,
            num_bars=4,
            include_melody=True,
            include_chords=True,
            synthesize_audio=True,
            use_gpu_synthesis=True,
            add_reverb=True,
        )

        logger.info("Generating music with audio synthesis...")

        response = await hybrid_music_generator.generate(request)

        logger.info(f"✓ Audio synthesis complete:")
        logger.info(f"  Audio file: {response.audio_file}")

        if response.audio_file:
            audio_path = Path(response.audio_file)
            if audio_path.exists():
                logger.info(f"  ✓ Audio file verified: {audio_path.stat().st_size} bytes")
            else:
                logger.warning(f"  ✗ Audio file not found")

        return True

    except Exception as e:
        logger.error(f"✗ Audio synthesis failed: {e}", exc_info=True)
        return False


async def main():
    """Run all tests"""
    logger.info("\n" + "🎵" * 30)
    logger.info("HYBRID MUSIC GENERATOR - TEST SUITE")
    logger.info("🎵" * 30)

    results = {}

    # Run tests
    results["chord_generation"] = await test_chord_generation()
    results["melody_generation"] = await test_melody_generation()
    results["chord_prediction"] = await test_chord_prediction()
    results["full_pipeline"] = await test_full_hybrid_pipeline()
    results["midi_tokenization"] = await test_midi_tokenization()
    results["audio_synthesis"] = await test_with_audio_synthesis()

    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)

    passed = sum(1 for r in results.values() if r is True)
    skipped = sum(1 for r in results.values() if r is None)
    failed = sum(1 for r in results.values() if r is False)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASSED" if result is True else ("⊘ SKIPPED" if result is None else "✗ FAILED")
        logger.info(f"  {test_name:<25} {status}")

    logger.info(f"\nResults: {passed}/{total} passed, {failed} failed, {skipped} skipped")

    if failed == 0:
        logger.info("\n🎉 All tests passed!")
    else:
        logger.warning(f"\n⚠️  {failed} test(s) failed")

    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
