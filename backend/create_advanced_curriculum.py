#!/usr/bin/env python
"""Create Advanced Gospel Piano Curriculum

Generates expert-level gospel piano exercises with:
- Complex extended chords (9ths, 11ths, 13ths)
- Altered dominants (#9, b9, #11, b13)
- Upper structure triads
- Reharmonizations
- Gospel runs and fills
- Polychords
"""

import asyncio
import json
import uuid
from datetime import datetime

from app.database.session import async_session_maker
from app.database.curriculum_models import (
    Curriculum,
    CurriculumModule,
    CurriculumLesson,
    CurriculumExercise,
)


async def create_advanced_curriculum():
    """Create advanced gospel piano curriculum"""

    print("=" * 80)
    print("🎹 Creating ADVANCED Gospel Piano Curriculum")
    print("=" * 80)

    async with async_session_maker() as session:
        # Create curriculum
        curriculum = Curriculum(
            id=str(uuid.uuid4()),
            user_id=1,
            title="Advanced Gospel Piano - Mastery & Improvisation",
            description="Expert-level gospel piano covering advanced voicings, reharmonization, runs, and professional-level improvisation techniques",
            duration_weeks=16,
            current_week=1,
            status='active',
            ai_model_used='expert_template',
        )
        session.add(curriculum)

        print(f"\n📚 Curriculum: {curriculum.title}")
        print(f"   Duration: {curriculum.duration_weeks} weeks")
        print(f"   Level: ADVANCED/EXPERT")

        # Module 1: Advanced Extended Chords
        print("\n📘 MODULE 1: Advanced Extended Chords & Alterations")

        module1 = CurriculumModule(
            id=str(uuid.uuid4()),
            curriculum_id=curriculum.id,
            title="Advanced Extended Chords & Alterations",
            description="Master complex extended chords, altered dominants, and sophisticated voicing techniques",
            theme="advanced_harmony",
            order_index=0,
            start_week=1,
            end_week=5,
            outcomes_json=json.dumps([
                "Play all extended chords (9ths, 11ths, 13ths) fluently",
                "Use altered dominants for tension and release",
                "Apply upper structure triads",
                "Reharmonize standard progressions"
            ]),
        )
        session.add(module1)

        # Lesson 1: Extended Chord Mastery
        lesson1 = CurriculumLesson(
            id=str(uuid.uuid4()),
            module_id=module1.id,
            title="Extended Chord Mastery - 9ths, 11ths, 13ths",
            description="Deep dive into extended chord voicings and their applications in gospel",
            week_number=1,
            theory_content_json=json.dumps({
                "summary": "Extended chords add sophisticated color and modern sound to gospel progressions",
                "key_points": [
                    "9th chords: Add 2nd scale degree above root",
                    "11th chords: Include 4th scale degree for suspended quality",
                    "13th chords: Full harmonic spectrum with 6th scale degree",
                    "Voice leading: Smooth transitions between extensions"
                ]
            }),
            concepts_json=json.dumps([
                "Extended voicings",
                "Color tones",
                "Upper extensions",
                "Chord stacking"
            ]),
            estimated_duration_minutes=60,
        )
        session.add(lesson1)

        # Exercise 1: Extended ii-V-I with 9ths and 13ths
        ex1 = CurriculumExercise(
            id=str(uuid.uuid4()),
            lesson_id=lesson1.id,
            title="Extended ii-V-I Progression",
            description="Classic ii-V-I with rich 9th and 13th voicings",
            order_index=0,
            exercise_type="progression",
            content_json=json.dumps({
                "chords": ["Dm11", "G13", "Cmaj9", "Am11"],
                "key": "C",
                "roman_numerals": ["ii11", "V13", "Imaj9", "vi11"],
                "voicing_style": "advanced_gospel",
                "hand": "both",
                "extensions": {
                    "Dm11": "D-F-A-C-E-G",
                    "G13": "G-B-D-F-A-E",
                    "Cmaj9": "C-E-G-B-D",
                    "Am11": "A-C-E-G-B-D"
                }
            }),
            difficulty="advanced",
            estimated_duration_minutes=20,
            target_bpm=85,
            next_review_at=datetime.utcnow(),
        )
        session.add(ex1)

        # Exercise 2: Altered Dominants
        ex2 = CurriculumExercise(
            id=str(uuid.uuid4()),
            lesson_id=lesson1.id,
            title="Altered Dominant Resolution",
            description="Use altered dominants (b9, #9, #11, b13) for maximum tension",
            order_index=1,
            exercise_type="progression",
            content_json=json.dumps({
                "chords": ["Dm9", "G7b9", "Cmaj13", "C7#9"],
                "key": "C",
                "voicing_style": "altered_dominants",
                "hand": "both",
                "alterations": {
                    "G7b9": "G-B-D-F-Ab (b9)",
                    "C7#9": "C-E-G-Bb-D# (#9)"
                }
            }),
            difficulty="advanced",
            estimated_duration_minutes=18,
            target_bpm=75,
            next_review_at=datetime.utcnow(),
        )
        session.add(ex2)

        # Exercise 3: Upper Structure Triads
        ex3 = CurriculumExercise(
            id=str(uuid.uuid4()),
            lesson_id=lesson1.id,
            title="Upper Structure Triad Voicings",
            description="Stack triads on top of bass notes for rich, contemporary sound",
            order_index=2,
            exercise_type="progression",
            content_json=json.dumps({
                "chords": ["Cmaj9", "Fmaj13", "Bm7b5", "E7alt"],
                "key": "C",
                "voicing_style": "upper_structures",
                "hand": "both",
                "upper_structures": {
                    "Cmaj9": "Em triad over C bass",
                    "Fmaj13": "G major triad over F bass",
                    "E7alt": "Ab triad over E bass"
                }
            }),
            difficulty="expert",
            estimated_duration_minutes=22,
            target_bpm=70,
            next_review_at=datetime.utcnow(),
        )
        session.add(ex3)

        # Module 2: Gospel Runs & Fills
        print("   ✅ 3 exercises created")
        print("\n📘 MODULE 2: Gospel Runs, Fills & Improvisation")

        module2 = CurriculumModule(
            id=str(uuid.uuid4()),
            curriculum_id=curriculum.id,
            title="Gospel Runs, Fills & Improvisation",
            description="Master authentic gospel runs, fills, and spontaneous improvisation techniques",
            theme="gospel_runs",
            order_index=1,
            start_week=6,
            end_week=10,
            outcomes_json=json.dumps([
                "Execute professional gospel runs between chords",
                "Create spontaneous fills and embellishments",
                "Improvise over standard progressions",
                "Develop personal gospel style"
            ]),
        )
        session.add(module2)

        # Lesson 2: Gospel Runs
        lesson2 = CurriculumLesson(
            id=str(uuid.uuid4()),
            module_id=module2.id,
            title="Signature Gospel Runs & Passing Chords",
            description="Learn the classic gospel runs that connect chords smoothly",
            week_number=6,
            theory_content_json=json.dumps({
                "summary": "Gospel runs use passing tones, chromatic movement, and rhythmic patterns",
                "key_points": [
                    "Chromatic approach: Target chord tones from half step above/below",
                    "Scalar runs: Use major/minor scales between chord changes",
                    "Passing chords: Add diminished/dominant chords between main chords",
                    "Rhythmic variation: Triplets, 16th notes, syncopation"
                ]
            }),
            concepts_json=json.dumps([
                "Chromatic runs",
                "Passing tones",
                "Diminished transitions",
                "Rhythmic fills"
            ]),
            estimated_duration_minutes=65,
        )
        session.add(lesson2)

        # Exercise 4: Chromatic Run Progression
        ex4 = CurriculumExercise(
            id=str(uuid.uuid4()),
            lesson_id=lesson2.id,
            title="Chromatic Gospel Run in C",
            description="Classic chromatic run connecting I to IV chord",
            order_index=0,
            exercise_type="progression",
            content_json=json.dumps({
                "chords": ["Cmaj7", "Dbdim7", "Dm7", "Ebdim7", "Em7", "Fmaj9"],
                "key": "C",
                "voicing_style": "gospel_runs",
                "hand": "both",
                "run_pattern": "chromatic_ascending",
                "passing_chords": ["Dbdim7", "Ebdim7"]
            }),
            difficulty="advanced",
            estimated_duration_minutes=25,
            target_bpm=90,
            next_review_at=datetime.utcnow(),
        )
        session.add(ex4)

        # Exercise 5: Pentatonic Run Fills
        ex5 = CurriculumExercise(
            id=str(uuid.uuid4()),
            lesson_id=lesson2.id,
            title="Pentatonic Fill Patterns",
            description="Use pentatonic scales for authentic gospel fills",
            order_index=1,
            exercise_type="progression",
            content_json=json.dumps({
                "chords": ["Cmaj9", "Am11", "Fmaj13", "G13sus4"],
                "key": "C",
                "voicing_style": "pentatonic_fills",
                "hand": "both",
                "scale_used": "C major pentatonic",
                "fill_points": ["After Cmaj9", "After Am11", "End of phrase"]
            }),
            difficulty="advanced",
            estimated_duration_minutes=20,
            target_bpm=95,
            next_review_at=datetime.utcnow(),
        )
        session.add(ex5)

        # Module 3: Reharmonization & Substitutions
        print("   ✅ 2 exercises created")
        print("\n📘 MODULE 3: Reharmonization & Chord Substitutions")

        module3 = CurriculumModule(
            id=str(uuid.uuid4()),
            curriculum_id=curriculum.id,
            title="Reharmonization & Advanced Substitutions",
            description="Transform simple progressions with sophisticated reharmonization techniques",
            theme="reharmonization",
            order_index=2,
            start_week=11,
            end_week=16,
            outcomes_json=json.dumps([
                "Reharmonize hymns and worship songs",
                "Use tritone substitutions fluently",
                "Apply modal interchange chords",
                "Create unique harmonic arrangements"
            ]),
        )
        session.add(module3)

        # Lesson 3: Reharmonization
        lesson3 = CurriculumLesson(
            id=str(uuid.uuid4()),
            module_id=module3.id,
            title="Advanced Reharmonization Techniques",
            description="Transform basic progressions into sophisticated harmonic journeys",
            week_number=11,
            theory_content_json=json.dumps({
                "summary": "Reharmonization adds harmonic interest while preserving melody",
                "key_points": [
                    "Tritone substitution: Replace V7 with bII7",
                    "Modal interchange: Borrow chords from parallel minor",
                    "Secondary dominants: Add V7/x chords",
                    "Pedal tones: Sustain bass note under changing harmony"
                ]
            }),
            concepts_json=json.dumps([
                "Tritone substitution",
                "Modal interchange",
                "Secondary dominants",
                "Harmonic substitution"
            ]),
            estimated_duration_minutes=70,
        )
        session.add(lesson3)

        # Exercise 6: Tritone Substitution
        ex6 = CurriculumExercise(
            id=str(uuid.uuid4()),
            lesson_id=lesson3.id,
            title="Tritone Substitution Mastery",
            description="Replace standard V7 chords with tritone substitutes",
            order_index=0,
            exercise_type="progression",
            content_json=json.dumps({
                "chords": ["Cmaj9", "Am11", "Db7#11", "Cmaj13"],
                "key": "C",
                "voicing_style": "tritone_sub",
                "hand": "both",
                "substitution": {
                    "original": "G7",
                    "substitute": "Db7#11",
                    "reason": "Tritone away from G7, leads smoothly to C"
                }
            }),
            difficulty="expert",
            estimated_duration_minutes=25,
            target_bpm=80,
            next_review_at=datetime.utcnow(),
        )
        session.add(ex6)

        # Exercise 7: Modal Interchange
        ex7 = CurriculumExercise(
            id=str(uuid.uuid4()),
            lesson_id=lesson3.id,
            title="Modal Interchange Colors",
            description="Borrow chords from parallel minor for darker, richer sound",
            order_index=1,
            exercise_type="progression",
            content_json=json.dumps({
                "chords": ["Cmaj9", "Ab13", "Fm9", "G7sus4", "Cmaj13"],
                "key": "C",
                "voicing_style": "modal_interchange",
                "hand": "both",
                "borrowed_chords": {
                    "Ab13": "bVI from C minor",
                    "Fm9": "iv from C minor"
                },
                "color": "darker, emotional"
            }),
            difficulty="expert",
            estimated_duration_minutes=28,
            target_bpm=75,
            next_review_at=datetime.utcnow(),
        )
        session.add(ex7)

        # Exercise 8: Complex Reharmonization
        ex8 = CurriculumExercise(
            id=str(uuid.uuid4()),
            lesson_id=lesson3.id,
            title="Complete Hymn Reharmonization",
            description="Full reharmonization of Amazing Grace with advanced techniques",
            order_index=2,
            exercise_type="progression",
            content_json=json.dumps({
                "chords": [
                    "Cmaj9", "F#m7b5", "Fmaj13", "C7#9",
                    "Fmaj9", "Bb13", "Em11", "Am9",
                    "Dm11", "Db7#11", "Cmaj13"
                ],
                "key": "C",
                "voicing_style": "full_reharmonization",
                "hand": "both",
                "techniques_used": [
                    "Secondary dominants",
                    "Tritone substitution",
                    "Modal interchange",
                    "Extended voicings"
                ],
                "original_song": "Amazing Grace"
            }),
            difficulty="expert",
            estimated_duration_minutes=35,
            target_bpm=68,
            next_review_at=datetime.utcnow(),
        )
        session.add(ex8)

        await session.commit()
        await session.refresh(curriculum)

        print("   ✅ 3 exercises created")
        print("\n" + "=" * 80)
        print("✅ ADVANCED CURRICULUM CREATED")
        print("=" * 80)
        print(f"\n🎯 Curriculum ID: {curriculum.id}")
        print(f"   Title: {curriculum.title}")
        print(f"   Modules: 3")
        print(f"   Lessons: 3")
        print(f"   Exercises: 8")
        print(f"   Duration: {curriculum.duration_weeks} weeks")
        print(f"   Level: ADVANCED/EXPERT")

        print("\n📊 Breakdown:")
        print("   Module 1: Extended Chords (3 exercises)")
        print("   Module 2: Gospel Runs (2 exercises)")
        print("   Module 3: Reharmonization (3 exercises)")

        print("\n💡 Techniques Covered:")
        print("   ✅ 9th, 11th, 13th chord voicings")
        print("   ✅ Altered dominants (b9, #9, #11)")
        print("   ✅ Upper structure triads")
        print("   ✅ Chromatic runs")
        print("   ✅ Passing chords")
        print("   ✅ Tritone substitutions")
        print("   ✅ Modal interchange")
        print("   ✅ Complete reharmonization")

        print("\n🎹 Ready to generate musical files!")
        print("=" * 80)

        return curriculum


if __name__ == "__main__":
    asyncio.run(create_advanced_curriculum())
