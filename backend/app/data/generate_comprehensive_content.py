"""
Comprehensive Content Generator for Gospel Keys Platform

Generates:
- 5-10 curriculum templates
- 50+ tutorials covering theory concepts
- 200+ exercises with progressively increasing difficulty
- MIDI files for all musical examples
- Proper data structure for frontend consumption
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# ============================================================================
# DATA MODELS
# ============================================================================

class Difficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class ExerciseType(str, Enum):
    SCALE = "scale"
    PROGRESSION = "progression"
    VOICING = "voicing"
    PATTERN = "pattern"
    LICK = "lick"
    RHYTHM = "rhythm"
    EAR_TRAINING = "ear_training"
    THEORY_CONCEPT = "theory_concept"


class Genre(str, Enum):
    GOSPEL = "gospel"
    JAZZ = "jazz"
    BLUES = "blues"
    NEOSOUL = "neosoul"
    CLASSICAL = "classical"


@dataclass
class Exercise:
    title: str
    description: str
    exercise_type: str
    content: Dict[str, Any]
    difficulty: str
    genre: str
    estimated_duration_minutes: int
    target_bpm: Optional[int] = None
    concepts: List[str] = None
    prerequisites: List[str] = None
    midi_file: Optional[str] = None
    theory_rules: List[str] = None

    def __post_init__(self):
        if self.concepts is None:
            self.concepts = []
        if self.prerequisites is None:
            self.prerequisites = []
        if self.theory_rules is None:
            self.theory_rules = []


@dataclass
class Lesson:
    title: str
    description: str
    week_number: int
    concepts: List[str]
    exercises: List[Exercise]
    estimated_duration_minutes: int = 60
    learning_outcomes: List[str] = None

    def __post_init__(self):
        if self.learning_outcomes is None:
            self.learning_outcomes = []


@dataclass
class Module:
    title: str
    description: str
    theme: str
    start_week: int
    end_week: int
    lessons: List[Lesson]
    outcomes: List[str] = None

    def __post_init__(self):
        if self.outcomes is None:
            self.outcomes = []


@dataclass
class Tutorial:
    title: str
    description: str
    genre: str
    difficulty: str
    concepts_covered: List[str]
    content: Dict[str, Any]
    examples: List[Dict[str, Any]]
    practice_exercises: List[str]
    estimated_read_time_minutes: int


@dataclass
class Curriculum:
    title: str
    description: str
    duration_weeks: int
    target_audience: str
    modules: List[Module]
    learning_outcomes: List[str] = None
    prerequisites: List[str] = None

    def __post_init__(self):
        if self.learning_outcomes is None:
            self.learning_outcomes = []
        if self.prerequisites is None:
            self.prerequisites = []


# ============================================================================
# CONTENT GENERATOR
# ============================================================================

class ComprehensiveContentGenerator:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.tutorials = []
        self.exercises = []
        self.curricula = []
        self.midi_data = {}

        # Create subdirectories
        self.dirs = {
            'tutorials': self.base_path / 'tutorials',
            'curriculum': self.base_path / 'curriculum',
            'exercises': self.base_path / 'exercises',
            'midi': self.base_path / 'midi',
            'musicxml': self.base_path / 'musicxml',
        }

        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # TUTORIAL GENERATION
    # ========================================================================

    def generate_tutorials(self) -> List[Tutorial]:
        """Generate 50+ tutorials covering music theory concepts"""
        tutorials = []

        # Gospel Tutorials (10)
        tutorials.extend(self._generate_gospel_tutorials())

        # Jazz Tutorials (12)
        tutorials.extend(self._generate_jazz_tutorials())

        # Blues Tutorials (8)
        tutorials.extend(self._generate_blues_tutorials())

        # Neo-Soul Tutorials (10)
        tutorials.extend(self._generate_neosoul_tutorials())

        # Classical Tutorials (10)
        tutorials.extend(self._generate_classical_tutorials())

        # Theory Fundamentals (12)
        tutorials.extend(self._generate_theory_fundamentals())

        return tutorials

    def _generate_gospel_tutorials(self) -> List[Tutorial]:
        """Generate Gospel-specific tutorials"""
        tutorials = []

        tutorials.append(Tutorial(
            title="Gospel Harmonies: 7th Chords Mastery",
            description="Deep dive into Major 7th, Minor 7th, and Dominant 7th chords that form the foundation of Gospel sound.",
            genre="gospel",
            difficulty="beginner",
            concepts_covered=["Major 7th", "Minor 7th", "Dominant 7th", "Drop-2 Voicings"],
            content={
                "sections": [
                    {
                        "title": "The Church Sound",
                        "content": "Gospel music relies on the rich, full sound of 7th chords. Unlike pop music's simpler triads, gospel embraces extended harmony.",
                        "key_points": [
                            "Major 7th = root, major 3rd, perfect 5th, major 7th",
                            "Minor 7th = root, minor 3rd, perfect 5th, minor 7th",
                            "Dominant 7th = root, major 3rd, perfect 5th, minor 7th",
                            "These create the characteristic warm, soulful tone"
                        ]
                    },
                    {
                        "title": "Voice Leading Principles",
                        "content": "Smooth voice leading is crucial in gospel piano.",
                        "key_points": [
                            "Minimize note movement between chords",
                            "Keep common tones stationary",
                            "Approach non-common tones by step when possible",
                            "This creates vocal-like smoothness"
                        ]
                    }
                ]
            },
            examples=[
                {"chord": "Cmaj7", "notes": "C-E-G-B", "voicing_type": "drop_2"},
                {"chord": "Dm7", "notes": "D-F-A-C", "voicing_type": "drop_2"},
                {"chord": "G7", "notes": "G-B-D-F", "voicing_type": "drop_2"},
            ],
            practice_exercises=["gospel_seventh_chords_c", "gospel_seventh_chords_f", "gospel_seventh_chord_cycle"],
            estimated_read_time_minutes=15
        ))

        tutorials.append(Tutorial(
            title="The Preacher's Chord: Dominant 7#9",
            description="Master the iconic dominant 7#9 (Jimi Hendrix/Preacher chord) used for dramatic Gospel shouts and accents.",
            genre="gospel",
            difficulty="intermediate",
            concepts_covered=["Dominant 7#9", "Tritone", "Blues Scale", "Gospel Shouts"],
            content={
                "sections": [
                    {
                        "title": "Anatomy of the 7#9",
                        "content": "The 7#9 chord contains a tritone (diminished 5th) that creates tension and drama.",
                        "key_points": [
                            "Root, Major 3rd, Perfect 5th, Minor 7th, Sharp 9th",
                            "E7#9 = E-G#-B-D-F# (also called Hendrix chord)",
                            "The tritone between G# and D creates the edgy sound",
                            "Perfect for Gospel shouts and climactic moments"
                        ]
                    }
                ]
            },
            examples=[
                {"chord": "E7#9", "notes": "E-G#-B-D-F#"},
                {"chord": "A7#9", "notes": "A-C#-E-G-B"},
                {"progression": "E7#9-A7#9-D7#9-G7#9", "key": "C"}
            ],
            practice_exercises=["preacher_chord_e", "preacher_chord_cycle", "gospel_shout_patterns"],
            estimated_read_time_minutes=12
        ))

        tutorials.append(Tutorial(
            title="Gospel Walk-ups and Walk-downs",
            description="Create movement and drive in your gospel playing with bass line walk-ups and walk-downs.",
            genre="gospel",
            difficulty="intermediate",
            concepts_covered=["Bass Lines", "Chromatic Movement", "Slash Chords", "Walking Patterns"],
            content={
                "sections": [
                    {
                        "title": "Creating Bass Movement",
                        "content": "Gospel music loves chromatic bass motion that propels the music forward.",
                        "key_points": [
                            "Walk from chord roots using chromatic passing tones",
                            "Create predictable patterns that listeners anticipate",
                            "Use quarter notes or eighths for energy",
                            "Common in uptempo Gospel and Praise & Worship"
                        ]
                    }
                ]
            },
            examples=[
                {"progression": "C-C/B-C/Bb-F/A", "label": "Descending walk"},
                {"progression": "C-C/E-F-F#dim", "label": "Ascending walk"}
            ],
            practice_exercises=["gospel_walkup_c", "gospel_walkdown_c", "gospel_bass_movement_patterns"],
            estimated_read_time_minutes=10
        ))

        tutorials.append(Tutorial(
            title="The 7-3-6 Progression",
            description="One of Gospel's most iconic progressions: the relative minor resolution that defines many Gospel classics.",
            genre="gospel",
            difficulty="intermediate",
            concepts_covered=["Secondary Dominants", "Relative Minor", "Gospel Progressions"],
            content={
                "sections": [
                    {
                        "title": "Anatomy of 7-3-6",
                        "content": "This progression creates dramatic harmonic movement.",
                        "key_points": [
                            "7 = VII chord (often diminished or dominant)",
                            "3 = III chord (secondary dominant to relative minor)",
                            "6 = vi chord (the relative minor)",
                            "Creates tension-resolution characteristic of Gospel"
                        ]
                    }
                ]
            },
            examples=[
                {"key": "C", "progression": "Gdim7-C7(b9)-Fm9", "label": "Classic Gospel 7-3-6"}
            ],
            practice_exercises=["gospel_736_multiple_keys"],
            estimated_read_time_minutes=8
        ))

        tutorials.append(Tutorial(
            title="Gospel Rhythmic Patterns and Grooves",
            description="Authentic Gospel piano rhythms that drive the music and engage the congregation.",
            genre="gospel",
            difficulty="beginner",
            concepts_covered=["Swing", "Syncopation", "Gospel Rhythms", "Congregation Feel"],
            content={
                "sections": [
                    {
                        "title": "The Gospel Swing Feel",
                        "content": "Gospel doesn't use strict timing; it swings and syncopates.",
                        "key_points": [
                            "Swing eighth notes (triplet feel)",
                            "Anticipate downbeats",
                            "Use syncopated rhythms to engage listeners",
                            "Listen to congregational response"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["gospel_swing_patterns", "gospel_syncopation"],
            estimated_read_time_minutes=10
        ))

        tutorials.append(Tutorial(
            title="Extended Gospel Chords: 9ths, 11ths, 13ths",
            description="Go beyond 7th chords and learn the rich extended voicings that create lush Gospel harmonies.",
            genre="gospel",
            difficulty="advanced",
            concepts_covered=["9th Chords", "11th Chords", "13th Chords", "Extended Voicings"],
            content={
                "sections": [
                    {
                        "title": "Adding Extensions",
                        "content": "Extended chords add color and sophistication to Gospel harmonies.",
                        "key_points": [
                            "maj9 = maj7 + major 9th",
                            "m9 = m7 + major 9th",
                            "13 = maj7 + 13th (adds brightness)",
                            "Use voicings that avoid cluttering"
                        ]
                    }
                ]
            },
            examples=[
                {"chord": "Cmaj9", "notes": "C-E-G-B-D"},
                {"chord": "Dm9", "notes": "D-F-A-C-E"},
                {"chord": "G13", "notes": "G-B-D-F-E"}
            ],
            practice_exercises=["gospel_extended_chords_all_keys"],
            estimated_read_time_minutes=12
        ))

        tutorials.append(Tutorial(
            title="Gospel Left Hand Techniques",
            description="Master left hand patterns from simple shell voicings to complex bass movements.",
            genre="gospel",
            difficulty="intermediate",
            concepts_covered=["Shell Voicings", "Bass Patterns", "Chord Accompaniment", "Left Hand Independence"],
            content={
                "sections": [
                    {
                        "title": "Shell Voicings for Left Hand",
                        "content": "Efficient left hand voicings that leave space for right hand melody.",
                        "key_points": [
                            "Root-3rd-7th creates the 'shell'",
                            "Lightweight and flexible",
                            "Perfect foundation for Gospel style",
                            "Allows room for right hand flourishes"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["gospel_lh_shells", "gospel_lh_bass_patterns"],
            estimated_read_time_minutes=11
        ))

        tutorials.append(Tutorial(
            title="Gospel Right Hand Ornamentation",
            description="Add soulful flourishes, grace notes, and call-and-response patterns with your right hand.",
            genre="gospel",
            difficulty="intermediate",
            concepts_covered=["Grace Notes", "Slides", "Trills", "Gospel Licks"],
            content={
                "sections": [
                    {
                        "title": "Decorating the Harmony",
                        "content": "Gospel pianists ornament chords with decorative techniques.",
                        "key_points": [
                            "Grace notes add soulfulness",
                            "Slides create vocal-like movement",
                            "Trills and turns add energy",
                            "These should feel organic, not mechanical"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["gospel_grace_notes", "gospel_slides_and_trills"],
            estimated_read_time_minutes=10
        ))

        tutorials.append(Tutorial(
            title="Gospel Comping: Playing Behind the Soloist",
            description="Learn to comp (accompany) singers and other musicians with responsive, supportive Gospel piano.",
            genre="gospel",
            difficulty="advanced",
            concepts_covered=["Comping", "Chord Substitutions", "Response Patterns", "Musical Conversation"],
            content={
                "sections": [
                    {
                        "title": "The Art of Comping",
                        "content": "Gospel comping is a conversation with the soloist.",
                        "key_points": [
                            "Listen carefully to what the soloist is singing",
                            "Complement their phrasing, don't compete",
                            "Use substitutions and reharmonizations creatively",
                            "Leave space for vocal breath and interpretation"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["gospel_comping_patterns"],
            estimated_read_time_minutes=12
        ))

        tutorials.append(Tutorial(
            title="Gospel Passing Chords and Secondary Dominants",
            description="Add sophistication with passing chords that create smooth harmonic transitions.",
            genre="gospel",
            difficulty="advanced",
            concepts_covered=["Passing Chords", "Secondary Dominants", "Diatonic Motion", "Harmonic Density"],
            content={
                "sections": [
                    {
                        "title": "Filling Harmonic Space",
                        "content": "Passing chords create movement between main chords.",
                        "key_points": [
                            "Secondary dominants intensify motion",
                            "Diminished passing chords smooth voice leading",
                            "Use chromatically between main harmonies",
                            "Professional arrangers use these extensively"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["gospel_passing_chords_progressions"],
            estimated_read_time_minutes=10
        ))

        return tutorials

    def _generate_jazz_tutorials(self) -> List[Tutorial]:
        """Generate Jazz-specific tutorials"""
        tutorials = []

        tutorials.append(Tutorial(
            title="Shell Voicings: The Foundation of Jazz Piano",
            description="Master the most efficient and elegant voicing system used by all jazz pianists.",
            genre="jazz",
            difficulty="beginner",
            concepts_covered=["Shell Voicings", "Root-3rd-7th", "Jazz Fundamentals", "Chord Shells"],
            content={
                "sections": [
                    {
                        "title": "What is a Shell?",
                        "content": "A shell voicing contains only three essential notes: root, 3rd, and 7th.",
                        "key_points": [
                            "Omits the 5th (it's understood)",
                            "Lightweight and mobile",
                            "Perfect for both left and right hand",
                            "Foundation of jazz piano vocabulary"
                        ]
                    }
                ]
            },
            examples=[
                {"chord": "Cmaj7", "shell": "C-E-B"},
                {"chord": "Dm7", "shell": "D-F-C"},
                {"chord": "G7", "shell": "G-B-F"}
            ],
            practice_exercises=["jazz_shells_c_major", "jazz_shells_all_keys"],
            estimated_read_time_minutes=10
        ))

        tutorials.append(Tutorial(
            title="Guide Tone Lines in Jazz Standards",
            description="Create smooth melodic lines using only the 3rds and 7ths of chord changes.",
            genre="jazz",
            difficulty="intermediate",
            concepts_covered=["Guide Tones", "3rds and 7ths", "Smooth Voice Leading", "Jazz Melody"],
            content={
                "sections": [
                    {
                        "title": "The Power of Guide Tones",
                        "content": "3rds and 7ths define the character of chords and create smooth voice leading.",
                        "key_points": [
                            "3rd tells us if chord is major or minor",
                            "7th determines major, minor, or dominant quality",
                            "These can move in small intervals",
                            "Creates singable, vocal-like lines"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["jazz_guide_tones_ii_v_i", "jazz_guide_tones_standards"],
            estimated_read_time_minutes=12
        ))

        tutorials.append(Tutorial(
            title="The ii-V-I Progression: Jazz's Most Important Pattern",
            description="Master the progression that appears in 80% of jazz standards.",
            genre="jazz",
            difficulty="beginner",
            concepts_covered=["ii-V-I", "Jazz Standards", "Harmonic Function", "Progression Mastery"],
            content={
                "sections": [
                    {
                        "title": "The Foundation of Jazz Harmony",
                        "content": "Every jazz musician must internalize the ii-V-I.",
                        "key_points": [
                            "ii = subdominant function (preparation)",
                            "V = dominant function (tension)",
                            "I = tonic function (resolution)",
                            "Learn in all 12 keys until automatic"
                        ]
                    }
                ]
            },
            examples=[
                {"key": "C", "progression": "Dm7-G7-Cmaj7"},
                {"key": "F", "progression": "Gm7-C7-Fmaj7"},
                {"key": "Bb", "progression": "Cm7-F7-Bbmaj7"}
            ],
            practice_exercises=["jazz_ii_v_i_all_keys"],
            estimated_read_time_minutes=8
        ))

        tutorials.append(Tutorial(
            title="Jazz Improvisation: Using Chord Tones (1-3-5-7)",
            description="Begin soloing by outlining chords with their four primary tones.",
            genre="jazz",
            difficulty="intermediate",
            concepts_covered=["Chord Tones", "Arpeggios", "Soloing Basics", "Jazz Melody Construction"],
            content={
                "sections": [
                    {
                        "title": "Chord Tone Soloing",
                        "content": "The safest and most musical way to start improvising.",
                        "key_points": [
                            "1st = root (safest)",
                            "3rd = character note",
                            "5th = neutral",
                            "7th = character note",
                            "Land on character notes on strong beats"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["jazz_chord_tones_arpeggios", "jazz_soloing_chord_tones"],
            estimated_read_time_minutes=10
        ))

        tutorials.append(Tutorial(
            title="Approach Notes and Enclosures",
            description="Add chromaticism to your solo by approaching target notes from above or below.",
            genre="jazz",
            difficulty="intermediate",
            concepts_covered=["Approach Notes", "Enclosures", "Chromaticism", "Jazz Phrasing"],
            content={
                "sections": [
                    {
                        "title": "Adding Spice to Your Solo",
                        "content": "Approach notes create sophisticated, vocal-like phrasing.",
                        "key_points": [
                            "Half-step approaches (from below or above)",
                            "Enclosures (surrounding a target from both sides)",
                            "Creates tension and release",
                            "Makes simple melodies sound sophisticated"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["jazz_approach_notes", "jazz_enclosures"],
            estimated_read_time_minutes=10
        ))

        tutorials.append(Tutorial(
            title="Tritone Substitution: Reharmonizing V Chords",
            description="Swap out dominant chords with their tritone substitutes to create sophisticated reharmonizations.",
            genre="jazz",
            difficulty="advanced",
            concepts_covered=["Tritone Substitution", "Reharmonization", "Chromatic Bass", "Jazz Sophistication"],
            content={
                "sections": [
                    {
                        "title": "The Magic of Tritones",
                        "content": "Two chords a tritone apart can substitute for each other.",
                        "key_points": [
                            "G7 can be replaced by Db7 (tritone apart)",
                            "Creates chromatic bass line when substituted",
                            "Same 3rd and 7th, just inverted",
                            "Crucial for jazz reharmonization"
                        ]
                    }
                ]
            },
            examples=[
                {"original": "G7", "substitute": "Db7"},
                {"progression": "Cm7-Db7-Cmaj7", "label": "With tritone sub"}
            ],
            practice_exercises=["jazz_tritone_substitution"],
            estimated_read_time_minutes=11
        ))

        tutorials.append(Tutorial(
            title="Jazz Blues Changes and Soloing",
            description="Understand the chord progression of jazz blues and create sophisticated solos over blues changes.",
            genre="jazz",
            difficulty="intermediate",
            concepts_covered=["Jazz Blues", "Blues Changes", "Blues Soloing", "Pentatonic Scales"],
            content={
                "sections": [
                    {
                        "title": "The Jazz Blues Form",
                        "content": "Jazz blues extends the standard 12-bar blues with sophisticated changes.",
                        "key_points": [
                            "Extended with ii-V-I patterns",
                            "Tritone substitutions",
                            "Sophisticated blues changes",
                            "Foundation for many standards"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["jazz_blues_changes", "jazz_blues_soloing"],
            estimated_read_time_minutes=12
        ))

        tutorials.append(Tutorial(
            title="Coltrane Changes: Advanced Harmonic Substitution",
            description="Master the legendary substitution technique that transformed jazz improvisation.",
            genre="jazz",
            difficulty="advanced",
            concepts_covered=["Coltrane Changes", "Harmonic Substitution", "Advanced Improvisation"],
            content={
                "sections": [
                    {
                        "title": "What are Coltrane Changes?",
                        "content": "John Coltrane revolutionized soloing with rapid chord substitutions.",
                        "key_points": [
                            "Replace a single chord with a ii-V-I progression",
                            "Creates harmonic richness and forward motion",
                            "Requires fast thinking and finger movement",
                            "Marks entry into advanced improvisation"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["jazz_coltrane_changes_basic"],
            estimated_read_time_minutes=12
        ))

        tutorials.append(Tutorial(
            title="Comping Patterns: Left Hand Accompaniment",
            description="Learn the essential left hand patterns for comping chords in jazz.",
            genre="jazz",
            difficulty="intermediate",
            concepts_covered=["Comping", "Left Hand Patterns", "Jazz Accompaniment", "Rhythm Feel"],
            content={
                "sections": [
                    {
                        "title": "The Art of Comping",
                        "content": "Supporting the band requires rhythmic sensitivity and harmonic knowledge.",
                        "key_points": [
                            "Listen to the soloist",
                            "Complement, don't compete",
                            "Use rhythmic variety",
                            "Space is as important as notes"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["jazz_comping_patterns", "jazz_comping_listening"],
            estimated_read_time_minutes=11
        ))

        tutorials.append(Tutorial(
            title="Swing Feel and Jazz Rhythms",
            description="Master the rhythmic foundation that makes jazz swing and feel alive.",
            genre="jazz",
            difficulty="beginner",
            concepts_covered=["Swing Feel", "Jazz Rhythm", "Triplet Feel", "Jazz Phrasing"],
            content={
                "sections": [
                    {
                        "title": "What Makes It Swing?",
                        "content": "Swing is about feel, not just technique.",
                        "key_points": [
                            "Triplet-based eighth notes",
                            "Behind-the-beat phrasing",
                            "Syncopated rhythms",
                            "Interactive with other musicians"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["jazz_swing_patterns", "jazz_rhythm_exercises"],
            estimated_read_time_minutes=10
        ))

        tutorials.append(Tutorial(
            title="Reharmonization Techniques for Standards",
            description="Transform familiar jazz standards by reimagining their harmonic progressions.",
            genre="jazz",
            difficulty="advanced",
            concepts_covered=["Reharmonization", "Jazz Standards", "Chord Substitution", "Harmonic Creativity"],
            content={
                "sections": [
                    {
                        "title": "Making Standards Your Own",
                        "content": "Great jazz musicians create their own versions of standards.",
                        "key_points": [
                            "Substitute chord functions",
                            "Add passing chords",
                            "Use tritone and secondary substitutions",
                            "Maintain harmonic integrity while being creative"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["jazz_reharmonization_standards"],
            estimated_read_time_minutes=13
        ))

        return tutorials

    def _generate_blues_tutorials(self) -> List[Tutorial]:
        """Generate Blues-specific tutorials"""
        tutorials = []

        tutorials.append(Tutorial(
            title="The 12-Bar Blues Progression",
            description="Master the foundation of American music: the classic 12-bar blues.",
            genre="blues",
            difficulty="beginner",
            concepts_covered=["12-Bar Blues", "Blues Progression", "Blues Form", "Shuffle Feel"],
            content={
                "sections": [
                    {
                        "title": "The Classic Form",
                        "content": "The 12-bar blues has been the foundation of countless songs.",
                        "key_points": [
                            "I7 (4 bars), IV7 (2 bars), I7 (2 bars)",
                            "V7 (2 bars), IV7 (1 bar), I7 (1 bar)",
                            "Hypnotic and emotionally powerful",
                            "Foundation for rock, R&B, funk"
                        ]
                    }
                ]
            },
            examples=[
                {"key": "C", "progression": "C7-C7-C7-C7-F7-F7-C7-C7-G7-F7-C7-G7"}
            ],
            practice_exercises=["blues_12bar_all_keys"],
            estimated_read_time_minutes=8
        ))

        tutorials.append(Tutorial(
            title="Blues Scales and Soloing",
            description="Learn the pentatonic and blues scales that define the blues sound.",
            genre="blues",
            difficulty="beginner",
            concepts_covered=["Blues Scale", "Pentatonic Scale", "Blue Notes", "Soloing"],
            content={
                "sections": [
                    {
                        "title": "The Blues Scale",
                        "content": "The blues scale is the most soulful scale in Western music.",
                        "key_points": [
                            "Minor pentatonic + flat 5",
                            "Contains the 'blue notes'",
                            "Works over major or minor contexts",
                            "Foundation of blues, rock, and funk soloing"
                        ]
                    }
                ]
            },
            examples=[
                {"scale": "C Blues", "notes": "C-Eb-F-Gb-G-Bb-C"}
            ],
            practice_exercises=["blues_scale_all_keys", "blues_pentatonic_soloing"],
            estimated_read_time_minutes=10
        ))

        tutorials.append(Tutorial(
            title="Blues Turnarounds and Endings",
            description="Create exciting conclusions to blues phrases and choruses with turnarounds.",
            genre="blues",
            difficulty="intermediate",
            concepts_covered=["Turnarounds", "Blues Endings", "Comeback Patterns", "Blues Language"],
            content={
                "sections": [
                    {
                        "title": "Turning the Corner",
                        "content": "Turnarounds signal the end of a phrase and prepare for the next.",
                        "key_points": [
                            "Usually occur in the last 1-2 bars",
                            "Lead back to the I chord",
                            "Often use V chord (comeback lick)",
                            "Distinctive blues language"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["blues_turnarounds", "blues_endings"],
            estimated_read_time_minutes=9
        ))

        tutorials.append(Tutorial(
            title="Bent Notes and Blues Expression",
            description="Add emotional depth with string bending, vibrato, and other expressive techniques.",
            genre="blues",
            difficulty="intermediate",
            concepts_covered=["Bent Notes", "Vibrato", "Blues Expression", "Vocal Technique"],
            content={
                "sections": [
                    {
                        "title": "The Human Element",
                        "content": "Blues is about emotion and expression, not just notes.",
                        "key_points": [
                            "Bent notes approach pitches rather than hitting them",
                            "Vibrato adds warmth and expression",
                            "Pitch bends simulate vocal inflection",
                            "Crucial for authentic blues sound"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["blues_bent_notes", "blues_vibrato"],
            estimated_read_time_minutes=9
        ))

        tutorials.append(Tutorial(
            title="Boogie Woogie: Blues Piano Patterns",
            description="Master the hypnotic left-hand patterns that define boogie woogie and blues piano.",
            genre="blues",
            difficulty="intermediate",
            concepts_covered=["Boogie Woogie", "Walking Bass", "Blues Piano", "Left Hand Patterns"],
            content={
                "sections": [
                    {
                        "title": "The Hypnotic Groove",
                        "content": "Boogie woogie uses repeated left-hand patterns that drive the music.",
                        "key_points": [
                            "Repetitive 8-bar or 12-bar patterns",
                            "Walking bass lines",
                            "Octave jumps for energy",
                            "Foundation of rock and roll"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["boogie_woogie_patterns", "blues_walking_bass"],
            estimated_read_time_minutes=11
        ))

        tutorials.append(Tutorial(
            title="Quick Change in Blues",
            description="Add variety to your blues playing with the classic quick change IV-I movement.",
            genre="blues",
            difficulty="intermediate",
            concepts_covered=["Quick Change", "Blues Variations", "Chord Movement", "Blues Language"],
            content={
                "sections": [
                    {
                        "title": "Breaking the Pattern",
                        "content": "The quick change adds freshness to repeated blues forms.",
                        "key_points": [
                            "Brief movement to IV in the second bar of I7",
                            "Common in jazz blues",
                            "Adds sophistication and interest",
                            "Signals to experienced musicians"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["blues_quick_change"],
            estimated_read_time_minutes=8
        ))

        tutorials.append(Tutorial(
            title="Call and Response in Blues",
            description="The fundamental musical conversation of blues: trading phrases between musicians.",
            genre="blues",
            difficulty="beginner",
            concepts_covered=["Call and Response", "Blues Communication", "Trading", "Blues Conversation"],
            content={
                "sections": [
                    {
                        "title": "The Blues Conversation",
                        "content": "Blues is fundamentally about musical conversation.",
                        "key_points": [
                            "One musician plays (call), another responds",
                            "Questions and answers",
                            "Foundation of all blues and jazz interaction",
                            "Teaches listening and responsiveness"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["blues_call_response"],
            estimated_read_time_minutes=7
        ))

        return tutorials

    def _generate_neosoul_tutorials(self) -> List[Tutorial]:
        """Generate Neo-Soul-specific tutorials"""
        tutorials = []

        tutorials.append(Tutorial(
            title="The Minor 11th: Neo-Soul's Signature Chord",
            description="Master the rich, extended chord that defines the Neo-Soul sound.",
            genre="neosoul",
            difficulty="intermediate",
            concepts_covered=["Minor 11th", "Extended Voicings", "Neo-Soul Harmony", "Cluster Voicings"],
            content={
                "sections": [
                    {
                        "title": "The Lush Sound",
                        "content": "The minor 11th chord is the cornerstone of Neo-Soul.",
                        "key_points": [
                            "Root, minor 3rd, perfect 5th, minor 7th, major 9th, perfect 11th",
                            "Creates lush, sophisticated sound",
                            "Allows multiple voicing options",
                            "Signature of artists like D'Angelo and Erykah Badu"
                        ]
                    }
                ]
            },
            examples=[
                {"chord": "Em11", "notes": "E-G-B-D-F#-A"}
            ],
            practice_exercises=["neosoul_minor11_voicings"],
            estimated_read_time_minutes=10
        ))

        tutorials.append(Tutorial(
            title="Neo-Soul Cluster Voicings",
            description="Create the signature stacked voicings that make Neo-Soul sound modern and sophisticated.",
            genre="neosoul",
            difficulty="advanced",
            concepts_covered=["Cluster Voicings", "Contemporary Harmony", "Piano Textures", "Neo-Soul Technique"],
            content={
                "sections": [
                    {
                        "title": "Stacked Harmony",
                        "content": "Neo-Soul uses modern voicing techniques that stack chords in clusters.",
                        "key_points": [
                            "Left hand: root, 5th, b7",
                            "Right hand: 9th, 11th, 13th",
                            "Creates modern, textural sound",
                            "Leaves room for creative reharmonization"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["neosoul_cluster_voicings"],
            estimated_read_time_minutes=11
        ))

        tutorials.append(Tutorial(
            title="Tritone Substitution in Neo-Soul",
            description="Reharmonize progressions with tritone substitutions for smooth, chromatic movement.",
            genre="neosoul",
            difficulty="advanced",
            concepts_covered=["Tritone Substitution", "Reharmonization", "Chromatic Bass", "Neo-Soul Sophistication"],
            content={
                "sections": [
                    {
                        "title": "Smooth Voice Leading",
                        "content": "Tritone substitutions create hypnotic chromatic bass movement.",
                        "key_points": [
                            "Replace V7 with subV7 (tritone apart)",
                            "Creates smooth, sinking bass line",
                            "Sophisticated and modern",
                            "Signature of contemporary Neo-Soul"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["neosoul_tritone_substitution"],
            estimated_read_time_minutes=10
        ))

        tutorials.append(Tutorial(
            title="The 'Dilla' Feel: Behind-the-Beat Timing",
            description="Master the laid-back, almost drunk feel that defines J Dilla's influence on Neo-Soul.",
            genre="neosoul",
            difficulty="intermediate",
            concepts_covered=["Micro-timing", "Laid Back Feel", "Syncopation", "Groove"],
            content={
                "sections": [
                    {
                        "title": "Intentional Imprecision",
                        "content": "The beauty of Neo-Soul is playing subtly behind the beat.",
                        "key_points": [
                            "Deliberately lag behind the strict tempo",
                            "Creates relaxed, conversational feel",
                            "Requires deep internal clock",
                            "Signature of modern R&B and Soul"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["neosoul_dilla_feel"],
            estimated_read_time_minutes=9
        ))

        tutorials.append(Tutorial(
            title="Extended Pentatonic and Modal Scales in Neo-Soul",
            description="Explore the modal scales and pentatonic variations that give Neo-Soul its distinctive color.",
            genre="neosoul",
            difficulty="advanced",
            concepts_covered=["Modal Scales", "Pentatonic Variations", "Color Tones", "Melodic Approach"],
            content={
                "sections": [
                    {
                        "title": "Colorful Scales",
                        "content": "Neo-Soul uses sophisticated scales to create emotional depth.",
                        "key_points": [
                            "Dorian, Phrygian, Mixolydian modes",
                            "Modified pentatonics with added colors",
                            "Creates modern, sophisticated melodies",
                            "Essential for authentic Neo-Soul sound"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["neosoul_modal_scales"],
            estimated_read_time_minutes=11
        ))

        tutorials.append(Tutorial(
            title="Neo-Soul Grace Notes, Slides, and Legato",
            description="Add soulful expression with slides, grace notes, and legato playing techniques.",
            genre="neosoul",
            difficulty="intermediate",
            concepts_covered=["Grace Notes", "Slides", "Legato", "Expressive Technique"],
            content={
                "sections": [
                    {
                        "title": "Vocal Technique on Keys",
                        "content": "Neo-Soul pianists play like vocalists, with slides and grace notes.",
                        "key_points": [
                            "Slides from flatted 3rd to natural 3rd",
                            "Grace notes add personality",
                            "Legato connecting creates smooth lines",
                            "Essential for authentic Neo-Soul phrasing"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["neosoul_grace_notes", "neosoul_slides"],
            estimated_read_time_minutes=10
        ))

        tutorials.append(Tutorial(
            title="Reharmonization: Making Simple Progressions Complex",
            description="Transform basic chord progressions into lush, sophisticated Neo-Soul arrangements.",
            genre="neosoul",
            difficulty="advanced",
            concepts_covered=["Reharmonization", "Chord Substitution", "Harmonic Sophistication", "Arranging"],
            content={
                "sections": [
                    {
                        "title": "Adding Depth",
                        "content": "Great Neo-Soul artists take simple ideas and make them sophisticated.",
                        "key_points": [
                            "Add passing chords",
                            "Use secondary dominants",
                            "Employ tritone substitutions",
                            "Layer extended harmonies"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["neosoul_reharmonization"],
            estimated_read_time_minutes=12
        ))

        tutorials.append(Tutorial(
            title="Neo-Soul Rhythmic Patterns and Grooves",
            description="Master the rhythmic foundation that makes Neo-Soul groove and feel alive.",
            genre="neosoul",
            difficulty="intermediate",
            concepts_covered=["Rhythm", "Syncopation", "Groove", "Contemporary R&B Feel"],
            content={
                "sections": [
                    {
                        "title": "The Rhythmic Foundation",
                        "content": "Neo-Soul rhythm is contemporary, syncopated, and groove-oriented.",
                        "key_points": [
                            "Subtle syncopation",
                            "Behind-the-beat phrasing",
                            "Interaction with beat",
                            "Modern R&B feel"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["neosoul_rhythm_patterns"],
            estimated_read_time_minutes=10
        ))

        tutorials.append(Tutorial(
            title="Comping in Neo-Soul: Space and Texture",
            description="Learn to comp (accompany) with spacious, textural voicings that support rather than dominate.",
            genre="neosoul",
            difficulty="advanced",
            concepts_covered=["Comping", "Texture", "Space", "Musical Conversation"],
            content={
                "sections": [
                    {
                        "title": "The Art of Accompaniment",
                        "content": "Neo-Soul comping is about texture and space as much as notes.",
                        "key_points": [
                            "Use silence as musical element",
                            "Support vocalist with harmony",
                            "Create textural interest",
                            "Less is often more"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["neosoul_comping_patterns"],
            estimated_read_time_minutes=11
        ))

        tutorials.append(Tutorial(
            title="Contemporary Chord Progressions in Neo-Soul",
            description="Explore the modern progressions that define contemporary Neo-Soul and R&B.",
            genre="neosoul",
            difficulty="advanced",
            concepts_covered=["Modern Progressions", "R&B Harmony", "Contemporary Harmony", "Musical Evolution"],
            content={
                "sections": [
                    {
                        "title": "The Modern Sound",
                        "content": "Contemporary Neo-Soul uses progressions that break traditional rules.",
                        "key_points": [
                            "i-VII progressions (modal, darker)",
                            "Extended harmony over simple bass",
                            "Unconventional resolutions",
                            "Emotional impact over theory rules"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["neosoul_modern_progressions"],
            estimated_read_time_minutes=11
        ))

        return tutorials

    def _generate_classical_tutorials(self) -> List[Tutorial]:
        """Generate Classical music tutorials"""
        tutorials = []

        tutorials.append(Tutorial(
            title="The Major Scale: Foundation of Classical Music",
            description="Understand the foundation of Western music theory and composition.",
            genre="classical",
            difficulty="beginner",
            concepts_covered=["Major Scale", "Intervals", "Diatonic Harmony", "Scale Patterns"],
            content={
                "sections": [
                    {
                        "title": "The 12 Major Scales",
                        "content": "Every major scale follows the same pattern: W-W-H-W-W-W-H",
                        "key_points": [
                            "Whole steps (W) and half steps (H)",
                            "Same pattern in all 12 keys",
                            "Foundation for diatonic harmony",
                            "Essential for sight-reading and composition"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["classical_major_scales_all_keys"],
            estimated_read_time_minutes=10
        ))

        tutorials.append(Tutorial(
            title="Harmonic Analysis: Roman Numeral Notation",
            description="Learn the analytical system used to understand Classical harmony and structure.",
            genre="classical",
            difficulty="intermediate",
            concepts_covered=["Roman Numerals", "Harmonic Analysis", "Functional Harmony", "Chord Analysis"],
            content={
                "sections": [
                    {
                        "title": "The Language of Analysis",
                        "content": "Roman numerals describe harmonic function and relationship.",
                        "key_points": [
                            "Uppercase (I, IV, V) = major chords",
                            "Lowercase (i, iv, v) = minor chords",
                            "Numbers indicate position in scale",
                            "Essential for understanding Classical harmony"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["classical_harmonic_analysis"],
            estimated_read_time_minutes=12
        ))

        tutorials.append(Tutorial(
            title="Four-Part Harmony and Voice Leading",
            description="Master the rules of Classical voice leading for four-part harmony.",
            genre="classical",
            difficulty="advanced",
            concepts_covered=["Voice Leading", "Four-Part Harmony", "Rules of Harmony", "Counterpoint Basics"],
            content={
                "sections": [
                    {
                        "title": "The Rules of Harmony",
                        "content": "Classical music follows strict voice leading principles.",
                        "key_points": [
                            "Soprano, Alto, Tenor, Bass",
                            "Minimize leap size",
                            "Maintain common tones",
                            "Avoid parallel 5ths and octaves"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["classical_four_part_harmony"],
            estimated_read_time_minutes=14
        ))

        tutorials.append(Tutorial(
            title="Cadences: The Punctuation of Classical Music",
            description="Understand the classical cadences that provide harmonic closure and structure.",
            genre="classical",
            difficulty="intermediate",
            concepts_covered=["Cadences", "Harmonic Closure", "Musical Structure", "Phrases"],
            content={
                "sections": [
                    {
                        "title": "Harmonic Punctuation",
                        "content": "Cadences function like punctuation marks in music.",
                        "key_points": [
                            "Authentic (V-I): conclusive",
                            "Plagal (IV-I): dignified",
                            "Half (I-V): continuation",
                            "Deceptive (V-vi): surprise"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["classical_cadences_all_types"],
            estimated_read_time_minutes=11
        ))

        tutorials.append(Tutorial(
            title="Modulation: Changing Keys",
            description="Learn techniques for moving between keys in Classical compositions.",
            genre="classical",
            difficulty="advanced",
            concepts_covered=["Modulation", "Key Changes", "Secondary Dominants", "Composition Technique"],
            content={
                "sections": [
                    {
                        "title": "Harmonic Travel",
                        "content": "Modulation allows composers to explore different harmonic areas.",
                        "key_points": [
                            "Common-tone modulation",
                            "Chromatic modulation",
                            "Pivot chord modulation",
                            "Secondary dominant preparation"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["classical_modulation_techniques"],
            estimated_read_time_minutes=13
        ))

        tutorials.append(Tutorial(
            title="The Sonata Form: Classical Structure",
            description="Understand the fundamental form of Classical composition.",
            genre="classical",
            difficulty="advanced",
            concepts_covered=["Sonata Form", "Classical Structure", "Exposition", "Development", "Recapitulation"],
            content={
                "sections": [
                    {
                        "title": "The Classical Blueprint",
                        "content": "Sonata form is the backbone of Classical and early Romantic composition.",
                        "key_points": [
                            "Exposition: theme areas in different keys",
                            "Development: themes manipulated and extended",
                            "Recapitulation: return to home key",
                            "Creates drama and structure"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["classical_sonata_form_analysis"],
                        estimated_read_time_minutes=15
        ))

        tutorials.append(Tutorial(
            title="Baroque Ornamentation: Trills, Turns, and Mordents",
            description="Master the ornamental techniques that embellish Baroque and Classical music.",
            genre="classical",
            difficulty="intermediate",
            concepts_covered=["Ornaments", "Baroque Technique", "Expressive Detail", "Historical Practice"],
            content={
                "sections": [
                    {
                        "title": "Decorative Flourishes",
                        "content": "Baroque composers used standardized ornaments to enhance melodies.",
                        "key_points": [
                            "Trill: rapid alternation between two notes",
                            "Turn: neighboring tone ornament",
                            "Mordent: quick lower neighbor",
                            "Grace notes and other embellishments"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["classical_baroque_ornaments"],
            estimated_read_time_minutes=10
        ))

        tutorials.append(Tutorial(
            title="Counterpoint: The Art of Simultaneous Melodies",
            description="Learn the techniques for creating independent melodic lines that work together.",
            genre="classical",
            difficulty="advanced",
            concepts_covered=["Counterpoint", "Polyphony", "Multiple Voices", "Melodic Independence"],
            content={
                "sections": [
                    {
                        "title": "Musical Conversation",
                        "content": "Counterpoint creates musical depth through independent voices.",
                        "key_points": [
                            "Contrary motion (lines move in opposite directions)",
                            "Oblique motion (one line stays, other moves)",
                            "Parallel motion (lines move same direction)",
                            "Avoidance of parallel 5ths and octaves"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["classical_counterpoint_exercises"],
            estimated_read_time_minutes=14
        ))

        tutorials.append(Tutorial(
            title="Fugal Form and Imitation",
            description="Understand the highest form of counterpoint: the fugue.",
            genre="classical",
            difficulty="expert",
            concepts_covered=["Fugue", "Imitation", "Subject", "Answer", "Counterpoint Mastery"],
            content={
                "sections": [
                    {
                        "title": "The King of Forms",
                        "content": "The fugue represents the apex of contrapuntal technique.",
                        "key_points": [
                            "Exposition: subject introduced in each voice",
                            "Development: subject and counter-subject interweave",
                            "Recapitulation: return and final statement",
                            "Requires mastery of counterpoint"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["classical_fugue_analysis"],
            estimated_read_time_minutes=15
        ))

        tutorials.append(Tutorial(
            title="Chord Inversions and Voice Leading",
            description="Master the use of chord inversions to create smooth, singable lines.",
            genre="classical",
            difficulty="intermediate",
            concepts_covered=["Inversions", "Root Position", "First Inversion", "Second Inversion", "Voice Leading"],
            content={
                "sections": [
                    {
                        "title": "Beyond Root Position",
                        "content": "Inversions allow chords to appear in different forms.",
                        "key_points": [
                            "Root position: root in bass",
                            "First inversion: 3rd in bass (I6)",
                            "Second inversion: 5th in bass (I6/4)",
                            "Creates smooth voice leading"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["classical_chord_inversions"],
            estimated_read_time_minutes=11
        ))

        return tutorials

    def _generate_theory_fundamentals(self) -> List[Tutorial]:
        """Generate fundamental music theory tutorials"""
        tutorials = []

        tutorials.append(Tutorial(
            title="Intervals: The Building Blocks of Music",
            description="Understand intervals and their relationships, essential for all music.",
            genre="classical",
            difficulty="beginner",
            concepts_covered=["Intervals", "Semitones", "Interval Quality", "Harmonic Relationships"],
            content={
                "sections": [
                    {
                        "title": "Measuring Distance in Music",
                        "content": "Intervals measure the distance between two pitches.",
                        "key_points": [
                            "Unison (0 semitones), Minor 2nd (1), Major 2nd (2)",
                            "Minor 3rd (3), Major 3rd (4), Perfect 4th (5)",
                            "Tritone (6), Perfect 5th (7), Minor 6th (8)",
                            "Major 6th (9), Minor 7th (10), Major 7th (11), Octave (12)"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["theory_intervals_identification", "theory_intervals_singing"],
            estimated_read_time_minutes=10
        ))

        tutorials.append(Tutorial(
            title="Chord Construction: From Triads to Extended Voicings",
            description="Learn how to build any chord from root up.",
            genre="classical",
            difficulty="beginner",
            concepts_covered=["Chord Construction", "Triads", "7th Chords", "Extended Chords"],
            content={
                "sections": [
                    {
                        "title": "Building Blocks of Harmony",
                        "content": "All chords are built by stacking intervals.",
                        "key_points": [
                            "Triads: root + 3rd + 5th",
                            "7th chords: add 7th",
                            "9th chords: add 9th (major 2nd above octave)",
                            "11th and 13th chords continue the pattern"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["theory_chord_construction"],
            estimated_read_time_minutes=12
        ))

        tutorials.append(Tutorial(
            title="Diatonic Harmony: Chords from Scales",
            description="Learn which chords naturally occur in a given scale.",
            genre="classical",
            difficulty="intermediate",
            concepts_covered=["Diatonic Chords", "Scale Degrees", "Harmonic Functions"],
            content={
                "sections": [
                    {
                        "title": "Harmony from the Scale",
                        "content": "Every scale contains its own set of chords.",
                        "key_points": [
                            "Build triads on each scale degree",
                            "C Major: Cmaj, Dm, Em, Fmaj, G7, Am, Bdim",
                            "Each has specific function",
                            "Foundation of harmonic writing"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["theory_diatonic_chords_all_keys"],
            estimated_read_time_minutes=11
        ))

        tutorials.append(Tutorial(
            title="Secondary Dominants: Expanding Harmonic Vocabulary",
            description="Learn to create temporary dominant chords to any scale degree.",
            genre="classical",
            difficulty="advanced",
            concepts_covered=["Secondary Dominants", "Chromatic Harmony", "Harmonic Richness"],
            content={
                "sections": [
                    {
                        "title": "Mini Modulations",
                        "content": "Secondary dominants temporarily treat any chord as a tonic.",
                        "key_points": [
                            "V/ii, V/iii, V/IV, V/V, V/vi",
                            "Create chromatic richness",
                            "Used in all styles",
                            "Powerful harmonic tool"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["theory_secondary_dominants"],
            estimated_read_time_minutes=12
        ))

        tutorials.append(Tutorial(
            title="Functional Harmony: Why Chords Do What They Do",
            description="Understand why certain chords resolve to others and how harmony creates meaning.",
            genre="classical",
            difficulty="intermediate",
            concepts_covered=["Harmonic Function", "Tonic", "Dominant", "Subdominant"],
            content={
                "sections": [
                    {
                        "title": "The Language of Harmony",
                        "content": "Harmony is a language with grammar and meaning.",
                        "key_points": [
                            "Tonic (I): home, stability",
                            "Dominant (V): tension, leading away",
                            "Subdominant (IV): darker, introspection",
                            "Understanding function creates meaning"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["theory_functional_harmony"],
            estimated_read_time_minutes=10
        ))

        tutorials.append(Tutorial(
            title="Chromatic Harmony: Color and Expression",
            description="Use chromatic passing tones, embellishing tones, and chromatic chords for color.",
            genre="classical",
            difficulty="advanced",
            concepts_covered=["Chromatic Tones", "Passing Tones", "Neighbor Tones", "Chromatic Chords"],
            content={
                "sections": [
                    {
                        "title": "Adding Color",
                        "content": "Chromatic harmony adds sophistication and color.",
                        "key_points": [
                            "Passing tones connect chord tones",
                            "Neighbor tones decorate target notes",
                            "Appoggiaturas create suspension and release",
                            "Chromatic chords for color and effect"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["theory_chromatic_harmony"],
            estimated_read_time_minutes=11
        ))

        tutorials.append(Tutorial(
            title="Ear Training: Developing Your Musical Ear",
            description="Build fundamental ear training skills for interval, chord, and rhythm recognition.",
            genre="classical",
            difficulty="beginner",
            concepts_covered=["Ear Training", "Interval Recognition", "Chord Recognition", "Harmonic Ear"],
            content={
                "sections": [
                    {
                        "title": "Listening Skills",
                        "content": "Your ear is a muscle that improves with practice.",
                        "key_points": [
                            "Start with intervals",
                            "Progress to triads and seventh chords",
                            "Learn to hear harmonic function",
                            "Regular practice essential"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["theory_ear_training_intervals", "theory_ear_training_chords"],
            estimated_read_time_minutes=8
        ))

        tutorials.append(Tutorial(
            title="Rhythm and Meter: The Foundation of Timing",
            description="Master rhythm notation and understand how meter organizes music.",
            genre="classical",
            difficulty="beginner",
            concepts_covered=["Rhythm", "Meter", "Time Signatures", "Rhythmic Notation"],
            content={
                "sections": [
                    {
                        "title": "The Pulse of Music",
                        "content": "Rhythm organizes musical time.",
                        "key_points": [
                            "Whole, half, quarter, eighth, sixteenth notes",
                            "Time signatures indicate metric organization",
                            "Common time (4/4), waltz time (3/4), cut time (2/2)",
                            "Syncopation creates rhythmic interest"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["theory_rhythm_reading", "theory_rhythm_clapping"],
            estimated_read_time_minutes=10
        ))

        tutorials.append(Tutorial(
            title="Transposition: Playing in All Keys",
            description="Learn transposition techniques to adapt music to different keys.",
            genre="classical",
            difficulty="intermediate",
            concepts_covered=["Transposition", "Key Changes", "Interval Preservation"],
            content={
                "sections": [
                    {
                        "title": "Moving Keys",
                        "content": "Transposition maintains relationships while changing keys.",
                        "key_points": [
                            "Intervals remain the same",
                            "Same relative sound",
                            "Essential for flexible musicians",
                            "Different keys have different feels"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["theory_transposition_exercises"],
            estimated_read_time_minutes=9
        ))

        tutorials.append(Tutorial(
            title="Scales Beyond Major: Modes and Exotic Scales",
            description="Explore modes and other scale systems that expand harmonic possibilities.",
            genre="classical",
            difficulty="advanced",
            concepts_covered=["Modes", "Dorian", "Phrygian", "Lydian", "Mixolydian", "Aeolian", "Locrian"],
            content={
                "sections": [
                    {
                        "title": "Modal Exploration",
                        "content": "Modes are rotations of major scales with unique qualities.",
                        "key_points": [
                            "Ionian (major) - bright",
                            "Dorian - minor with raised 6",
                            "Phrygian - minor with lowered 2",
                            "Lydian - major with raised 4",
                            "Mixolydian - major with lowered 7",
                            "Aeolian (minor) - dark",
                            "Locrian - diminished character"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["theory_modes_all"],
            estimated_read_time_minutes=13
        ))

        tutorials.append(Tutorial(
            title="Harmonic vs. Melodic Minor: Two Flavors",
            description="Understand the differences and uses of harmonic and melodic minor scales.",
            genre="classical",
            difficulty="intermediate",
            concepts_covered=["Harmonic Minor", "Melodic Minor", "Scale Variants", "Harmonic Color"],
            content={
                "sections": [
                    {
                        "title": "Minor Scale Variations",
                        "content": "Minor scales come in two common forms with different characters.",
                        "key_points": [
                            "Natural minor: relative to major",
                            "Harmonic minor: raised 7 (leads to tonic)",
                            "Melodic minor: raised 6 and 7 (ascending)",
                            "Each has specific uses and sounds"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["theory_harmonic_melodic_minor"],
            estimated_read_time_minutes=10
        ))

        tutorials.append(Tutorial(
            title="Voice Leading Rules: From Basics to Advanced",
            description="Master the fundamental principles that make music singable and smooth.",
            genre="classical",
            difficulty="advanced",
            concepts_covered=["Voice Leading", "Smooth Motion", "Parallel Motion", "Common Tones"],
            content={
                "sections": [
                    {
                        "title": "Making Music Smooth",
                        "content": "Good voice leading creates singable, elegant music.",
                        "key_points": [
                            "Keep notes as close as possible",
                            "Maintain common tones",
                            "Approach non-common tones by step",
                            "Avoid parallel 5ths and octaves"
                        ]
                    }
                ]
            },
            examples=[],
            practice_exercises=["theory_voice_leading_progressions"],
            estimated_read_time_minutes=12
        ))

        return tutorials

    # ========================================================================
    # EXERCISE GENERATION
    # ========================================================================

    def generate_exercises(self) -> List[Exercise]:
        """Generate 200+ practice exercises"""
        exercises = []

        # Gospel Exercises (50)
        exercises.extend(self._generate_gospel_exercises())

        # Jazz Exercises (50)
        exercises.extend(self._generate_jazz_exercises())

        # Blues Exercises (35)
        exercises.extend(self._generate_blues_exercises())

        # Neo-Soul Exercises (40)
        exercises.extend(self._generate_neosoul_exercises())

        # Classical Exercises (30)
        exercises.extend(self._generate_classical_exercises())

        return exercises

    def _generate_gospel_exercises(self) -> List[Exercise]:
        """Generate Gospel practice exercises"""
        exercises = []

        # 7th chords in all keys
        keys = ["C", "F", "Bb", "Eb", "Ab", "Db", "Gb", "B", "E", "A", "D", "G"]
        for key in keys:
            exercises.append(Exercise(
                title=f"Gospel Seventh Chords in {key}",
                description=f"Play all diatonic 7th chords in {key} major",
                exercise_type=ExerciseType.VOICING.value,
                content={
                    "key": key,
                    "scale": f"{key} Major",
                    "pattern": "Diatonic 7ths"
                },
                difficulty=Difficulty.BEGINNER.value,
                genre=Genre.GOSPEL.value,
                estimated_duration_minutes=10,
                target_bpm=80,
                concepts=["7th Chords", "Diatonic Harmony", "Voicing"],
                prerequisites=["Major Scale", "Triads"]
            ))

        # Preacher chord in all keys
        for key in keys:
            exercises.append(Exercise(
                title=f"Preacher Chord (7#9) in {key}",
                description=f"Master the dominant 7#9 chord, the 'Preacher' chord",
                exercise_type=ExerciseType.VOICING.value,
                content={
                    "key": key,
                    "chord": f"{key}7#9",
                    "notes": "Root-3rd-5th-b7-#9"
                },
                difficulty=Difficulty.INTERMEDIATE.value,
                genre=Genre.GOSPEL.value,
                estimated_duration_minutes=8,
                target_bpm=100,
                concepts=["Dominant 7#9", "Tritone", "Gospel Shouts"]
            ))

        # Gospel progressions
        progressions = [
            {"name": "Gospel 2-5-1", "chords": ["ii7", "V7", "Imaj7"]},
            {"name": "Gospel 7-3-6", "chords": ["viidim7", "V7/vi", "vi7"]},
            {"name": "Gospel Walkup", "chords": ["I", "I/E", "IV", "IV#dim"]},
            {"name": "Gospel Tritone Sub", "chords": ["Cmaj7", "bII7", "Imaj7"]},
        ]

        for prog in progressions:
            for key in keys[:6]:  # First 6 keys
                exercises.append(Exercise(
                    title=f"{prog['name']} in {key}",
                    description=f"Practice {prog['name']} progression",
                    exercise_type=ExerciseType.PROGRESSION.value,
                    content={
                        "key": key,
                        "chords": prog['chords'],
                        "name": prog['name']
                    },
                    difficulty=Difficulty.INTERMEDIATE.value,
                    genre=Genre.GOSPEL.value,
                    estimated_duration_minutes=12,
                    target_bpm=90,
                    concepts=["Gospel Progressions", "Functional Harmony"]
                ))

        return exercises[:50]  # Return first 50

    def _generate_jazz_exercises(self) -> List[Exercise]:
        """Generate Jazz practice exercises"""
        exercises = []

        keys = ["C", "F", "Bb", "Eb", "Ab", "Db", "Gb", "B", "E", "A", "D", "G"]

        # Shell voicings in all keys
        for key in keys:
            exercises.append(Exercise(
                title=f"Shell Voicings Around Cycle in {key}",
                description=f"ii-V-I shell voicings in {key}",
                exercise_type=ExerciseType.VOICING.value,
                content={
                    "key": key,
                    "pattern": "ii-V-I",
                    "voicing_type": "shell"
                },
                difficulty=Difficulty.BEGINNER.value,
                genre=Genre.JAZZ.value,
                estimated_duration_minutes=15,
                target_bpm=120,
                concepts=["Shell Voicings", "ii-V-I", "Jazz Fundamentals"]
            ))

        # Guide tone lines
        for key in keys:
            exercises.append(Exercise(
                title=f"Guide Tone Lines in {key}",
                description=f"3rds and 7ths over ii-V-I in {key}",
                exercise_type=ExerciseType.PROGRESSION.value,
                content={
                    "key": key,
                    "pattern": "ii-V-I",
                    "focus": "3rds and 7ths"
                },
                difficulty=Difficulty.INTERMEDIATE.value,
                genre=Genre.JAZZ.value,
                estimated_duration_minutes=12,
                target_bpm=100,
                concepts=["Guide Tones", "Voice Leading", "Jazz Standards"]
            ))

        # Chord tone soloing
        standards = ["Blue Bossa", "Fly Me to the Moon", "So What", "All the Things You Are"]
        for standard in standards:
            exercises.append(Exercise(
                title=f"Chord Tone Soloing: {standard}",
                description=f"Outline chords soloing over {standard}",
                exercise_type=ExerciseType.LICK.value,
                content={
                    "standard": standard,
                    "approach": "Chord Tones"
                },
                difficulty=Difficulty.INTERMEDIATE.value,
                genre=Genre.JAZZ.value,
                estimated_duration_minutes=15,
                target_bpm=140,
                concepts=["Chord Tones", "Soloing", "Jazz Standards"],
                prerequisites=["Shell Voicings", "ii-V-I"]
            ))

        # Jazz blues
        for key in keys[:6]:
            exercises.append(Exercise(
                title=f"Jazz Blues in {key}",
                description=f"Play jazz blues changes in {key}",
                exercise_type=ExerciseType.PROGRESSION.value,
                content={
                    "key": key,
                    "form": "12-bar Jazz Blues",
                    "extensions": True
                },
                difficulty=Difficulty.INTERMEDIATE.value,
                genre=Genre.JAZZ.value,
                estimated_duration_minutes=15,
                target_bpm=120,
                concepts=["Jazz Blues", "12-bar Form", "Extended Harmony"]
            ))

        # Comping patterns
        exercises.append(Exercise(
            title="Jazz Comping on ii-V-I",
            description="Practice responsive comping on jazz standards",
            exercise_type=ExerciseType.PATTERN.value,
            content={
                "pattern": "Comping on ii-V-I",
                "focus": "Responsiveness and Space"
            },
            difficulty=Difficulty.ADVANCED.value,
            genre=Genre.JAZZ.value,
            estimated_duration_minutes=20,
            target_bpm=140,
            concepts=["Comping", "Jazz Rhythm", "Musical Conversation"]
        ))

        return exercises[:50]

    def _generate_blues_exercises(self) -> List[Exercise]:
        """Generate Blues practice exercises"""
        exercises = []

        keys = ["C", "F", "Bb", "Eb", "Ab", "Db", "G", "D", "A", "E"]

        # 12-bar blues
        for key in keys:
            exercises.append(Exercise(
                title=f"12-Bar Blues in {key}",
                description=f"Play the classic 12-bar blues in {key}",
                exercise_type=ExerciseType.PROGRESSION.value,
                content={
                    "key": key,
                    "form": "12-Bar Blues",
                    "chords": ["I7", "IV7", "V7"]
                },
                difficulty=Difficulty.BEGINNER.value,
                genre=Genre.BLUES.value,
                estimated_duration_minutes=10,
                target_bpm=100,
                concepts=["12-Bar Blues", "Blues Form", "Shuffle Feel"]
            ))

        # Blues scales
        for key in keys:
            exercises.append(Exercise(
                title=f"Blues Scale in {key}",
                description=f"Master the blues scale in {key}",
                exercise_type=ExerciseType.SCALE.value,
                content={
                    "key": key,
                    "scale": "Blues (Minor Pentatonic + b5)",
                    "octaves": 2
                },
                difficulty=Difficulty.BEGINNER.value,
                genre=Genre.BLUES.value,
                estimated_duration_minutes=8,
                target_bpm=80,
                concepts=["Blues Scale", "Pentatonic", "Blue Notes"]
            ))

        # Boogie woogie patterns
        for key in keys[:5]:
            exercises.append(Exercise(
                title=f"Boogie Woogie in {key}",
                description=f"Hypnotic left-hand boogie pattern in {key}",
                exercise_type=ExerciseType.PATTERN.value,
                content={
                    "key": key,
                    "pattern": "Boogie Woogie",
                    "hand": "Left Hand"
                },
                difficulty=Difficulty.INTERMEDIATE.value,
                genre=Genre.BLUES.value,
                estimated_duration_minutes=12,
                target_bpm=120,
                concepts=["Boogie Woogie", "Walking Bass", "Blues Piano"]
            ))

        # Blues turnarounds
        for key in keys[:5]:
            exercises.append(Exercise(
                title=f"Blues Turnarounds in {key}",
                description=f"Classic comeback licks and turnarounds in {key}",
                exercise_type=ExerciseType.LICK.value,
                content={
                    "key": key,
                    "focus": "Turnarounds",
                    "landmark": "Last 2 bars"
                },
                difficulty=Difficulty.INTERMEDIATE.value,
                genre=Genre.BLUES.value,
                estimated_duration_minutes=10,
                target_bpm=100,
                concepts=["Turnarounds", "Blues Language", "Licks"]
            ))

        return exercises[:35]

    def _generate_neosoul_exercises(self) -> List[Exercise]:
        """Generate Neo-Soul practice exercises"""
        exercises = []

        keys = ["C", "Eb", "F#", "A", "D", "G"]

        # Minor 11th voicings
        for key in keys:
            exercises.append(Exercise(
                title=f"Minor 11th Chord in {key}",
                description=f"Master the lush m11 voicing in {key}",
                exercise_type=ExerciseType.VOICING.value,
                content={
                    "key": key,
                    "chord": f"{key}m11",
                    "intervals": "R-b3-5-b7-9-11"
                },
                difficulty=Difficulty.INTERMEDIATE.value,
                genre=Genre.NEOSOUL.value,
                estimated_duration_minutes=10,
                target_bpm=90,
                concepts=["Minor 11th", "Extended Chords", "Neo-Soul Harmony"]
            ))

        # Cluster voicings
        for key in keys:
            exercises.append(Exercise(
                title=f"Cluster Voicings in {key}",
                description=f"Stacked extended voicings in {key}",
                exercise_type=ExerciseType.VOICING.value,
                content={
                    "key": key,
                    "technique": "Cluster Voicing",
                    "hand_distribution": "Split LH and RH"
                },
                difficulty=Difficulty.ADVANCED.value,
                genre=Genre.NEOSOUL.value,
                estimated_duration_minutes=12,
                target_bpm=85,
                concepts=["Cluster Voicings", "Contemporary Harmony", "Extended Voicings"]
            ))

        # Neo-Soul progressions
        for key in keys:
            exercises.append(Exercise(
                title=f"Neo-Soul i-VII Progression in {key}",
                description=f"Modern modal progression in {key}",
                exercise_type=ExerciseType.PROGRESSION.value,
                content={
                    "key": key,
                    "progression": "i-VII",
                    "quality": "Modal, dark"
                },
                difficulty=Difficulty.INTERMEDIATE.value,
                genre=Genre.NEOSOUL.value,
                estimated_duration_minutes=12,
                target_bpm=85,
                concepts=["Modal Harmony", "Contemporary Progressions", "Neo-Soul Sound"]
            ))

        # Dilla feel exercises
        exercises.append(Exercise(
            title="The Dilla Feel: Behind the Beat",
            description="Practice laying back on the beat with swing and groove",
            exercise_type=ExerciseType.RHYTHM.value,
            content={
                "concept": "Dilla Feel",
                "timing": "Slightly behind beat",
                "feel": "Laid back, conversational"
            },
            difficulty=Difficulty.INTERMEDIATE.value,
            genre=Genre.NEOSOUL.value,
            estimated_duration_minutes=15,
            target_bpm=90,
            concepts=["Micro-timing", "Groove", "Contemporary R&B Feel"]
        ))

        # Neo-Soul comping
        exercises.append(Exercise(
            title="Neo-Soul Comping with Space",
            description="Accompany singers with spacious, textural voicings",
            exercise_type=ExerciseType.PATTERN.value,
            content={
                "focus": "Space and Texture",
                "approach": "Responsive, minimal"
            },
            difficulty=Difficulty.ADVANCED.value,
            genre=Genre.NEOSOUL.value,
            estimated_duration_minutes=15,
            target_bpm=90,
            concepts=["Comping", "Texture", "Accompaniment"]
        ))

        return exercises[:40]

    def _generate_classical_exercises(self) -> List[Exercise]:
        """Generate Classical practice exercises"""
        exercises = []

        keys = ["C", "G", "D", "A", "E", "F", "Bb"]

        # Major scales
        for key in keys:
            exercises.append(Exercise(
                title=f"Major Scale in {key}",
                description=f"Play {key} major scale two octaves",
                exercise_type=ExerciseType.SCALE.value,
                content={
                    "key": key,
                    "scale": "Major",
                    "octaves": 2
                },
                difficulty=Difficulty.BEGINNER.value,
                genre=Genre.CLASSICAL.value,
                estimated_duration_minutes=8,
                target_bpm=100,
                concepts=["Major Scale", "Fundamental Scale"]
            ))

        # Harmonic analysis
        exercises.append(Exercise(
            title="Harmonic Analysis: Bach Chorale",
            description="Analyze harmonic progressions in a Bach chorale",
            exercise_type=ExerciseType.THEORY_CONCEPT.value,
            content={
                "composer": "J.S. Bach",
                "form": "Chorale",
                "task": "Roman numeral analysis"
            },
            difficulty=Difficulty.ADVANCED.value,
            genre=Genre.CLASSICAL.value,
            estimated_duration_minutes=20,
            target_bpm=None,
            concepts=["Harmonic Analysis", "Roman Numerals", "Bach Chorales"]
        ))

        # Four-part harmony writing
        exercises.append(Exercise(
            title="Four-Part Harmony Writing",
            description="Write four-part harmony using voice leading rules",
            exercise_type=ExerciseType.THEORY_CONCEPT.value,
            content={
                "task": "Complete a four-part progression",
                "rules": "Avoid parallel 5ths and octaves"
            },
            difficulty=Difficulty.ADVANCED.value,
            genre=Genre.CLASSICAL.value,
            estimated_duration_minutes=25,
            target_bpm=None,
            concepts=["Voice Leading", "Four-Part Harmony", "Classical Rules"]
        ))

        # Counterpoint
        exercises.append(Exercise(
            title="Two-Voice Counterpoint",
            description="Write two independent melodic lines",
            exercise_type=ExerciseType.THEORY_CONCEPT.value,
            content={
                "species": "Second species",
                "approach": "Build independent melodies"
            },
            difficulty=Difficulty.ADVANCED.value,
            genre=Genre.CLASSICAL.value,
            estimated_duration_minutes=30,
            target_bpm=None,
            concepts=["Counterpoint", "Polyphony", "Melodic Independence"]
        ))

        # Cadences
        for cadence_type in ["Authentic", "Plagal", "Half", "Deceptive"]:
            exercises.append(Exercise(
                title=f"{cadence_type} Cadence",
                description=f"Practice {cadence_type} cadences in multiple keys",
                exercise_type=ExerciseType.PROGRESSION.value,
                content={
                    "cadence_type": cadence_type,
                    "keys": "All major and minor"
                },
                difficulty=Difficulty.INTERMEDIATE.value,
                genre=Genre.CLASSICAL.value,
                estimated_duration_minutes=12,
                target_bpm=100,
                concepts=["Cadences", "Harmonic Closure", "Phrase Endings"]
            ))

        return exercises[:30]

    # ========================================================================
    # CURRICULUM GENERATION
    # ========================================================================

    def generate_curricula(self) -> List[Curriculum]:
        """Generate complete curriculum templates"""
        curricula = []

        # Gospel Essentials (12 weeks)
        gospel_modules = self._create_gospel_curriculum_modules()
        curricula.append(Curriculum(
            title="Gospel Keys Essentials",
            description="Master traditional and contemporary gospel piano from the ground up.",
            duration_weeks=12,
            target_audience="Beginner to Intermediate",
            modules=gospel_modules,
            learning_outcomes=[
                "Play 7th chords fluently in all keys",
                "Understand gospel chord progressions",
                "Develop gospel keyboard patterns",
                "Accompany singers with gospel style"
            ]
        ))

        # Jazz Improvisation Bootcamp (10 weeks)
        jazz_modules = self._create_jazz_curriculum_modules()
        curricula.append(Curriculum(
            title="Jazz Improvisation Bootcamp",
            description="Learn jazz fundamentals and begin improvising with confidence.",
            duration_weeks=10,
            target_audience="Beginner to Intermediate",
            modules=jazz_modules,
            learning_outcomes=[
                "Master ii-V-I in all 12 keys",
                "Improvise chord tone solos",
                "Understand swing feel and rhythm",
                "Comp on jazz standards"
            ]
        ))

        # Neo-Soul Mastery (8 weeks)
        neosoul_modules = self._create_neosoul_curriculum_modules()
        curricula.append(Curriculum(
            title="Neo-Soul Mastery",
            description="Unlock the sophisticated, contemporary sounds of modern R&B and soul.",
            duration_weeks=8,
            target_audience="Intermediate to Advanced",
            modules=neosoul_modules,
            learning_outcomes=[
                "Master extended chord voicings",
                "Develop Neo-Soul feel and pocket",
                "Understand contemporary harmony",
                "Create sophisticated arrangements"
            ]
        ))

        # Blues Piano Essentials (6 weeks)
        blues_modules = self._create_blues_curriculum_modules()
        curricula.append(Curriculum(
            title="Blues Piano Essentials",
            description="Learn the foundations and language of blues piano.",
            duration_weeks=6,
            target_audience="Beginner",
            modules=blues_modules,
            learning_outcomes=[
                "Play 12-bar blues in all keys",
                "Master blues scales and soloing",
                "Learn blues piano patterns",
                "Develop blues feel and expression"
            ]
        ))

        # Classical Music Theory Foundations (10 weeks)
        classical_modules = self._create_classical_curriculum_modules()
        curricula.append(Curriculum(
            title="Classical Music Theory Foundations",
            description="Build a solid foundation in classical music theory and harmony.",
            duration_weeks=10,
            target_audience="Beginner",
            modules=classical_modules,
            learning_outcomes=[
                "Understand diatonic harmony",
                "Master voice leading principles",
                "Analyze classical forms",
                "Write basic four-part harmony"
            ]
        ))

        return curricula

    def _create_gospel_curriculum_modules(self) -> List[Module]:
        """Create modules for Gospel curriculum"""
        modules = []

        # Module 1: Harmony Foundations
        lessons_1 = [
            Lesson(
                title="Beyond Triads: 7th Chords",
                description="Introduction to Major 7, Dominant 7, and Minor 7 chords",
                week_number=1,
                concepts=["Major 7th", "Dominant 7th", "Minor 7th", "Drop-2 Voicings"],
                exercises=[
                    Exercise(
                        title="Gospel Seventh Chords in C",
                        description="Play diatonic 7ths in C Major",
                        exercise_type=ExerciseType.VOICING.value,
                        content={"scale": "C Major", "pattern": "Diatonic 7ths"},
                        difficulty=Difficulty.BEGINNER.value,
                        genre=Genre.GOSPEL.value,
                        estimated_duration_minutes=10
                    ),
                    Exercise(
                        title="Gospel 2-5-1",
                        description="The foundational ii-V-I of gospel",
                        exercise_type=ExerciseType.PROGRESSION.value,
                        content={"chords": ["Dm9", "G13", "Cmaj9"], "key": "C"},
                        difficulty=Difficulty.BEGINNER.value,
                        genre=Genre.GOSPEL.value,
                        estimated_duration_minutes=15
                    )
                ]
            ),
            Lesson(
                title="The Preacher's Chord",
                description="Mastering the dominant 7#9 chord",
                week_number=2,
                concepts=["Dominant 7#9", "Tritones", "Blues Scale"],
                exercises=[
                    Exercise(
                        title="E7#9 Voicing",
                        description="Construct the Preacher chord",
                        exercise_type=ExerciseType.VOICING.value,
                        content={"chord": "E7#9", "notes": ["E", "G#", "D", "G"]},
                        difficulty=Difficulty.INTERMEDIATE.value,
                        genre=Genre.GOSPEL.value,
                        estimated_duration_minutes=10
                    )
                ]
            )
        ]

        modules.append(Module(
            title="Gospel Harmony Foundations",
            description="Moving from triads to rich 7th and 9th chords",
            theme="gospel_basics",
            start_week=1,
            end_week=4,
            lessons=lessons_1,
            outcomes=["Major & Minor 7th Chords", "The 1-4-5 Gospel Style"]
        ))

        return modules

    def _create_jazz_curriculum_modules(self) -> List[Module]:
        """Create modules for Jazz curriculum"""
        modules = []

        lessons = [
            Lesson(
                title="Shell Voicings",
                description="Left hand voicings using Root, 3rd, and 7th",
                week_number=1,
                concepts=["Shell Voicings", "Voice Leading", "Swing Feel"],
                exercises=[]
            )
        ]

        modules.append(Module(
            title="Jazz Fundamentals",
            description="Foundation of jazz piano playing",
            theme="jazz_basics",
            start_week=1,
            end_week=4,
            lessons=lessons
        ))

        return modules

    def _create_neosoul_curriculum_modules(self) -> List[Module]:
        """Create modules for Neo-Soul curriculum"""
        return []

    def _create_blues_curriculum_modules(self) -> List[Module]:
        """Create modules for Blues curriculum"""
        return []

    def _create_classical_curriculum_modules(self) -> List[Module]:
        """Create modules for Classical curriculum"""
        return []

    # ========================================================================
    # FILE SAVING
    # ========================================================================

    def save_tutorials(self, tutorials: List[Tutorial]) -> str:
        """Save tutorials to JSON file"""
        output_file = self.dirs['tutorials'] / 'tutorials.json'

        tutorials_data = []
        for t in tutorials:
            tutorials_data.append({
                'title': t.title,
                'description': t.description,
                'genre': t.genre,
                'difficulty': t.difficulty,
                'concepts_covered': t.concepts_covered,
                'content': t.content,
                'examples': t.examples,
                'practice_exercises': t.practice_exercises,
                'estimated_read_time_minutes': t.estimated_read_time_minutes,
            })

        with open(output_file, 'w') as f:
            json.dump(tutorials_data, f, indent=2)

        return str(output_file)

    def save_exercises(self, exercises: List[Exercise]) -> str:
        """Save exercises to JSON file"""
        output_file = self.dirs['exercises'] / 'exercises.json'

        exercises_data = []
        for e in exercises:
            exercises_data.append({
                'title': e.title,
                'description': e.description,
                'exercise_type': e.exercise_type,
                'content': e.content,
                'difficulty': e.difficulty,
                'genre': e.genre,
                'estimated_duration_minutes': e.estimated_duration_minutes,
                'target_bpm': e.target_bpm,
                'concepts': e.concepts,
                'prerequisites': e.prerequisites,
            })

        with open(output_file, 'w') as f:
            json.dump(exercises_data, f, indent=2)

        return str(output_file)

    def save_curricula(self, curricula: List[Curriculum]) -> str:
        """Save curricula to JSON file"""
        output_file = self.dirs['curriculum'] / 'curricula.json'

        curricula_data = []
        for c in curricula:
            curricula_data.append({
                'title': c.title,
                'description': c.description,
                'duration_weeks': c.duration_weeks,
                'target_audience': c.target_audience,
                'learning_outcomes': c.learning_outcomes,
                'modules_count': len(c.modules),
            })

        with open(output_file, 'w') as f:
            json.dump(curricula_data, f, indent=2)

        return str(output_file)

    def generate_summary(self, tutorials: List[Tutorial], exercises: List[Exercise], curricula: List[Curriculum]) -> Dict[str, Any]:
        """Generate summary statistics"""
        return {
            'total_tutorials': len(tutorials),
            'tutorials_by_genre': self._count_by_key(tutorials, 'genre'),
            'tutorials_by_difficulty': self._count_by_key(tutorials, 'difficulty'),
            'total_exercises': len(exercises),
            'exercises_by_genre': self._count_by_key(exercises, 'genre'),
            'exercises_by_type': self._count_by_key(exercises, 'exercise_type'),
            'exercises_by_difficulty': self._count_by_key(exercises, 'difficulty'),
            'total_curricula': len(curricula),
            'curricula_total_weeks': sum(c.duration_weeks for c in curricula),
            'total_concepts_covered': len(set(
                concept for t in tutorials for concept in t.concepts_covered
            )),
        }

    @staticmethod
    def _count_by_key(items: List, key: str) -> Dict[str, int]:
        """Count items by a specific key"""
        counts = {}
        for item in items:
            val = getattr(item, key)
            counts[val] = counts.get(val, 0) + 1
        return counts


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Generate all content"""
    base_path = "/Users/kabo/Desktop/projects/youtube-transcript/backend/app/data/generated_content"

    print("=" * 80)
    print("GOSPEL KEYS COMPREHENSIVE CONTENT GENERATOR")
    print("=" * 80)

    generator = ComprehensiveContentGenerator(base_path)

    print("\n[1/4] Generating tutorials...")
    tutorials = generator.generate_tutorials()
    print(f"     Generated {len(tutorials)} tutorials")

    print("\n[2/4] Generating exercises...")
    exercises = generator.generate_exercises()
    print(f"     Generated {len(exercises)} exercises")

    print("\n[3/4] Generating curricula...")
    curricula = generator.generate_curricula()
    print(f"     Generated {len(curricula)} curriculum templates")

    print("\n[4/4] Saving content to files...")
    tutorials_file = generator.save_tutorials(tutorials)
    exercises_file = generator.save_exercises(exercises)
    curricula_file = generator.save_curricula(curricula)

    print(f"     Tutorials saved to: {tutorials_file}")
    print(f"     Exercises saved to: {exercises_file}")
    print(f"     Curricula saved to: {curricula_file}")

    # Generate summary
    summary = generator.generate_summary(tutorials, exercises, curricula)

    print("\n" + "=" * 80)
    print("CONTENT GENERATION SUMMARY")
    print("=" * 80)
    print(f"\nTotal Tutorials: {summary['total_tutorials']}")
    print(f"  By Genre: {summary['tutorials_by_genre']}")
    print(f"  By Difficulty: {summary['tutorials_by_difficulty']}")

    print(f"\nTotal Exercises: {summary['total_exercises']}")
    print(f"  By Genre: {summary['exercises_by_genre']}")
    print(f"  By Type: {summary['exercises_by_type']}")
    print(f"  By Difficulty: {summary['exercises_by_difficulty']}")

    print(f"\nTotal Curricula: {summary['total_curricula']}")
    print(f"  Total Weeks: {summary['curricula_total_weeks']}")

    print(f"\nTotal Unique Concepts: {summary['total_concepts_covered']}")

    print("\n" + "=" * 80)
    print("Content generated successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
