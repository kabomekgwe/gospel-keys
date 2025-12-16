"""
Master Curriculum Data
Contains all music theory templates, including expanded Gospel and new Funk genres.
"""

# Default DNA to use if an exercise is missing specific playback instructions
DEFAULT_PLAYBACK_DNA = {
    "velocity_range": (60, 80),
    "swing_percent": 0,
    "articulation": "legato",
    "bpm_range": (80, 100)
}

# --- NEW GENRE: FUNK ---

FUNK_MASTERY = {
    "title": "Funk & Groove Mastery",
    "description": "Develop a rhythmic pocket, master Clavinet-style articulation, and learn the secrets of New Orleans piano funk.",
    "modules": [
        {
            "title": "The Funk Pocket",
            "theme": "funk_rhythm",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["16th Note Subdivision", "Ghost Notes", "The 'One'"],
            "lessons": [
                {
                    "title": "Percussive Articulation",
                    "description": "Using the piano as a drum kit. Staccato stabs vs. ghost notes.",
                    "week_number": 1,
                    "concepts": ["Ghost Notes", "Staccato", "Subdivision"],
                    "exercises": [
                        {
                            "title": "Ghost Note Grid",
                            "description": "Alternating loud accents and soft ghost notes on a single chord.",
                            "exercise_type": "rhythm",
                            "difficulty": "beginner",
                            "playback_dna": {
                                "velocity_range": (30, 110), # Huge dynamic range for funk
                                "swing_percent": 55,         # Slight funk swing
                                "articulation": "staccato",
                                "bpm_range": (95, 105)
                            },
                            "content": {
                                "chord": "E9",
                                "pattern": "1e&a 2e&a (Accents on 1 and 'a' of 2)"
                            }
                        }
                    ]
                },
                {
                    "title": "Clavinet Fundamentals",
                    "description": "Adapting Clavinet techniques to the piano keys.",
                    "week_number": 2,
                    "concepts": ["Release Timing", "Bouncing Octaves"],
                    "exercises": [
                        {
                            "title": "Superstition Pattern",
                            "description": "The classic interlocking hands pattern.",
                            "exercise_type": "lick",
                            "playback_dna": {
                                "velocity_range": (70, 90),
                                "swing_percent": 50, # Straight 16ths
                                "articulation": "staccato", 
                            },
                            "content": {
                                "key": "Eb Minor",
                                "scale": "Eb Minor Pentatonic"
                            }
                        }
                    ]
                }
            ]
        },
        {
            "title": "New Orleans & Blues Funk",
            "theme": "nola_funk",
            "start_week": 5,
            "end_week": 8,
            "outcomes": ["Professor Longhair Rolls", "Dr. John Style 3rds", "Second Line Rhythm"],
            "lessons": [
                {
                    "title": "The Second Line Groove",
                    "description": "That 'in-between' shuffle feel from New Orleans.",
                    "week_number": 5,
                    "exercises": [
                        {
                            "title": "Rolling 3rds & 6ths",
                            "description": "Sliding grace notes into major 3rds (The 'Tipitina' sound).",
                            "exercise_type": "lick",
                            "playback_dna": {
                                "velocity_range": (60, 85),
                                "swing_percent": 66, # Heavy triplet swing
                                "articulation": "legato_slur"
                            },
                            "content": {
                                "technique": "Crushed Grace Notes",
                                "intervals": ["3rds", "6ths"]
                            }
                        }
                    ]
                }
            ]
        }
    ]
}

# --- EXTENDED CURRICULUM: GOSPEL ---

GOSPEL_KEYS_ESSENTIALS = {
    "title": "Gospel Keys Essentials",
    "description": "The definitive start to playing traditional and contemporary gospel.",
    "modules": [
        {
            "title": "Gospel Harmony Foundations",
            "description": "Moving from triads to the rich sound of 7th and 9th chords.",
            "theme": "gospel_basics",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["Major & Minor 7th Chords", "The 1-4-5 Gospel Style", "Basic Shout Patterns"],
            "lessons": [
                {
                    "title": "Beyond Triads: 7th Chords",
                    "week_number": 1,
                    "concepts": ["Major 7th", "Dominant 7th", "Minor 7th", "Drop-2 Voicings"],
                    "theory_content": {
                        "summary": "Gospel music relies heavily on 7th chords to create a fuller sound.",
                        "key_points": ["Add the 7th note to every triad", "Use inversions to keep common tones"]
                    },
                    "exercises": [
                        {
                            "title": "Diatonic 7th Chords in C",
                            "description": "Play all 7th chords in C Major (Cmaj7, Dm7, Em7...)",
                            "exercise_type": "scale",
                            "difficulty": "beginner",
                            "content": {"scale": "C Major", "pattern": "Diatonic 7ths"}
                        },
                        {
                            "title": "Gospel 2-5-1",
                            "description": "The foundational progression of gospel harmony.",
                            "exercise_type": "progression",
                            "difficulty": "beginner",
                            "content": {"chords": ["Dm9", "G13", "Cmaj9"], "key": "C"}
                        }
                    ]
                },
                {
                    "title": "The Preacher's Chord",
                    "week_number": 2,
                    "concepts": ["Dominant 7#9", "Tritones", "Blues Scale"],
                    "exercises": [
                        {
                            "title": "E7#9 Voicing",
                            "exercise_type": "voicing",
                            "content": {"chord": "E7#9", "notes": ["E", "G#", "D", "G"]},
                            "difficulty": "intermediate"
                        },
                        {
                            "title": "Preacher Chords in Cycle",
                            "exercise_type": "progression",
                            "content": {"chords": ["E7#9", "A7#9", "D7#9", "G7#9"], "key": "C"},
                            "difficulty": "intermediate"
                        }
                    ]
                }
            ]
        },
        {
            "title": "Gospel Progressions & Movements",
            "theme": "gospel_progressions",
            "start_week": 5,
            "end_week": 8,
            "outcomes": ["7-3-6 Progression", "Tritone Subs", "Gospel Waltz"],
            "lessons": [
                {
                    "title": "The 7-3-6 Progression",
                    "week_number": 5,
                    "concepts": ["Secondary Dominants", "Diminished Passing Chords"],
                    "exercises": [
                        {
                            "title": "7-3-6 in Ab",
                            "exercise_type": "progression",
                            "content": {
                                "key": "Ab",
                                "chords": ["Gdim7", "C7(b9)", "Fm9"],
                                "roman_numerals": ["vii°7/vi", "V7/vi", "vi7"]
                            },
                            "difficulty": "intermediate"
                        }
                    ]
                },
                {
                    "title": "Walk-ups and Walk-downs",
                    "week_number": 6,
                    "concepts": ["Bass Lines", "Slash Chords"],
                    "exercises": [
                        {
                            "title": "The 1 to 4 Walk-up",
                            "exercise_type": "progression",
                            "content": {
                                "key": "C",
                                "chords": ["C", "C/E", "F", "F#dim7", "C/G"],
                                "roman_numerals": ["I", "I/3", "IV", "#iv°7", "I/5"]
                            },
                            "difficulty": "intermediate"
                        }
                    ]
                }
            ]
        },
        # --- NEW ADVANCED MODULE ---
        {
            "title": "Advanced Gospel Harmony",
            "description": "Professional reharmonization techniques, talk music, and exotic passing chords.",
            "theme": "gospel_advanced",
            "start_week": 9,
            "end_week": 12,
            "outcomes": ["Tritone Substitutions", "Poly-Chords", "Talk Music"],
            "lessons": [
                {
                    "title": "Talk Music & Atmosphere",
                    "description": "Playing freely behind a speaker without disrupting the flow.",
                    "week_number": 9,
                    "concepts": ["Rubato", "Shells", "Sustained Tensions"],
                    "exercises": [
                        {
                            "title": "Rubato Flow in Db",
                            "description": "Free-time playing using lush major 9s and 13s.",
                            "exercise_type": "progression",
                            "playback_dna": {
                                "velocity_range": (30, 55),
                                "swing_percent": 0,
                                "articulation": "legato",
                                "rubato_factor": 0.8,
                                "bpm_range": (60, 70)
                            },
                            "content": {
                                "key": "Db",
                                "progression": "1-4-5 Free Flow"
                            },
                            "difficulty": "advanced"
                        }
                    ]
                },
                {
                    "title": "Tritone Substitutions",
                    "description": "Replacing dominant chords with their tritone opposite.",
                    "week_number": 10,
                    "concepts": ["Tritone Sub", "Chromatic Bass"],
                    "exercises": [
                        {
                            "title": "7-3-6 with Tritones",
                            "description": "Standard: Gdim -> C7 -> Fm. Advanced: Gdim -> Gb13(#11) -> Fm9.",
                            "exercise_type": "reharm",
                            "playback_dna": {
                                "velocity_range": (60, 80),
                                "swing_percent": 60,
                                "voicing_density": "high"
                            },
                            "content": {
                                "original": ["Gdim7", "C7alt", "Fm7"],
                                "reharm": ["Gdim7", "Gb13#11", "Fm9"]
                            },
                            "difficulty": "advanced"
                        }
                    ]
                }
            ]
        }
    ]
}

# --- EXISTING TEMPLATES ---

JAZZ_IMPROV_BOOTCAMP = {
    "title": "Jazz Improvisation Bootcamp",
    "description": "A step-by-step roadmap from basic swing to confident soloing.",
    "modules": [
        {
            "title": "Jazz Fundamentals",
            "theme": "jazz_basics",
            "start_week": 1,
            "end_week": 4,
            "lessons": [
                {
                    "title": "Shell Voicings (A & B Forms)",
                    "week_number": 1,
                    "concepts": ["Shell Voicings", "Voice Leading", "Swing Feel"],
                    "exercises": [
                        {
                            "title": "Shells around the Cycle",
                            "exercise_type": "voicing",
                            "content": {"pattern": "ii-V-I Cycle", "voicing_type": "shell"},
                            "difficulty": "beginner"
                        }
                    ]
                },
                {
                    "title": "Guide Tone Lines",
                    "week_number": 2,
                    "concepts": ["Guide Tones", "Thirds and Sevenths"],
                    "exercises": [
                        {
                            "title": "Guide Tones on Blue Bossa",
                            "exercise_type": "progression",
                            "content": {"key": "Cm", "chords": ["Cm7", "Fm7", "Dm7b5", "G7alt"]},
                            "difficulty": "intermediate"
                        }
                    ]
                }
            ]
        },
        {
            "title": "Beginning Improvisation",
            "theme": "jazz_improv",
            "start_week": 5,
            "end_week": 8,
            "lessons": [
                {
                    "title": "Arpeggio Soloing",
                    "week_number": 5,
                    "concepts": ["Chord Tones", "Arpeggios"],
                    "exercises": [
                        {
                            "title": "Arpeggios over 2-5-1",
                            "exercise_type": "scale",
                            "content": {"pattern": "1-3-5-7 Up, 7-5-3-1 Down", "key": "Bb"},
                            "difficulty": "intermediate"
                        }
                    ]
                },
                {
                    "title": "Approach Notes",
                    "week_number": 6,
                    "concepts": ["Chromatics", "Enclosures"],
                    "exercises": [
                        {
                            "title": "Half-step Approaches",
                            "exercise_type": "lick",
                            "content": {"pattern": "Chromatic Approach"},
                            "difficulty": "advanced"
                        }
                    ]
                }
            ]
        }
    ]
}

NEO_SOUL_MASTERY = {
    "title": "Neo-Soul Mastery",
    "description": "Unlock the smooth, laid-back sounds of R&B and Soul.",
    "modules": [
        {
            "title": "Neo-Soul Harmony",
            "theme": "neosoul_basics",
            "start_week": 1,
            "end_week": 4,
            "lessons": [
                {
                    "title": "The Minor 11th Chord",
                    "week_number": 1,
                    "concepts": ["Minor 9th", "Minor 11th", "Cluster Voicings"],
                    "exercises": [
                        {
                            "title": "Eb Minor 11 Deep Dive",
                            "exercise_type": "voicing",
                            "content": {"chord": "Ebm11", "notes": ["Eb", "Bb", "Db", "F", "Ab", "Bb"]},
                            "difficulty": "intermediate"
                        }
                    ]
                },
                {
                    "title": "Tritone Substitution",
                    "week_number": 2,
                    "exercises": [
                        {
                            "title": "Tritone Subs in 2-5-1",
                            "exercise_type": "progression",
                            "content": {
                                "chords": ["Dm9", "Db9#11", "Cmaj9"],
                                "roman_numerals": ["ii9", "subV7", "Imaj9"]
                            },
                            "difficulty": "advanced"
                        }
                    ]
                }
            ]
        },
        {
            "title": "Groove & Ornamentation",
            "theme": "neosoul_groove",
            "start_week": 5,
            "end_week": 8,
            "lessons": [
                {
                    "title": "The 'Dilla' Feel",
                    "week_number": 5,
                    "concepts": ["Micro-timing", "Syncopation"],
                    "exercises": [
                        {
                            "title": "Laid Back Scales",
                            "exercise_type": "rhythm",
                            "difficulty": "intermediate"
                        }
                    ]
                },
                {
                    "title": "Grace Notes & Slides",
                    "week_number": 6,
                    "concepts": ["Pentatonic Slides", "Crushed Notes"],
                    "exercises": [
                        {
                            "title": "Pentatonic Grace Notes",
                            "exercise_type": "lick",
                            "difficulty": "intermediate"
                        }
                    ]
                }
            ]
        }
    ]
}

CONTEMPORARY_WORSHIP = {
    "title": "Contemporary Worship Piano",
    "description": "Modern techniques for P&W music. Focus on Sus chords, pads, textures.",
    "modules": [
        {
            "title": "Worship Essentials",
            "theme": "worship_basics",
            "start_week": 1,
            "end_week": 4,
            "lessons": [
                {
                    "title": "Suspended Chords (Sus2 & Sus4)",
                    "week_number": 1,
                    "concepts": ["Sus2", "Sus4", "Add2"],
                    "exercises": [
                        {
                            "title": "Sus Chords in D Major",
                            "exercise_type": "voicing",
                            "content": {"key": "D", "chords": ["Dsus4", "D", "Asus4", "A"]},
                            "difficulty": "beginner"
                        }
                    ]
                },
                {
                    "title": "Slash Chords",
                    "week_number": 2,
                    "exercises": [
                        {
                            "title": "1 over 5 Slash Chords",
                            "exercise_type": "progression",
                            "difficulty": "intermediate"
                        }
                    ]
                }
            ]
        }
    ]
}

BLUES_MASTER_CLASS = {
    "title": "Blues Master Class",
    "description": "Master authentic blues piano from the ground up.",
    "modules": [
        {
            "title": "Blues Fundamentals",
            "theme": "blues_basics",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["12-Bar Blues Form", "Blues Scale Mastery", "Dominant 7th Voicings"],
            "lessons": [
                {
                    "title": "The 12-Bar Blues Form",
                    "week_number": 1,
                    "concepts": ["12-Bar Form", "Dominant 7ths", "Shuffle Feel"],
                    "exercises": [
                        {
                            "title": "Basic 12-Bar in C",
                            "exercise_type": "progression",
                            "content": {
                                "chords": ["C7", "C7", "C7", "C7", "F7", "F7", "C7", "C7", "G7", "F7", "C7", "G7"],
                                "key": "C"
                            },
                            "difficulty": "beginner"
                        }
                    ]
                },
                {
                    "title": "The Blues Scale",
                    "week_number": 2,
                    "concepts": ["Minor Pentatonic", "Blue Note (b5)", "Call and Response"],
                    "exercises": [
                        {
                            "title": "C Blues Scale Patterns",
                            "exercise_type": "scale",
                            "content": {"scale": "C Blues", "notes": ["C", "Eb", "F", "Gb", "G", "Bb", "C"]},
                            "difficulty": "beginner"
                        }
                    ]
                }
            ]
        },
        {
            "title": "Blues Turnarounds & Licks",
            "theme": "blues_advanced",
            "start_week": 5,
            "end_week": 8,
            "outcomes": ["Classic Turnarounds", "Intro Licks", "Ending Tags"],
            "lessons": [
                {
                    "title": "The Classic Turnaround",
                    "week_number": 5,
                    "concepts": ["Turnarounds", "Chromatic Movement", "Walking Bass"],
                    "exercises": [
                        {
                            "title": "Standard Blues Turnaround in C",
                            "exercise_type": "progression",
                            "content": {"chords": ["C7", "A7", "Dm7", "G7"], "key": "C"},
                            "difficulty": "intermediate"
                        }
                    ]
                }
            ]
        }
    ]
}

BERKLEE_JAZZ_ESSENTIALS = {
    "title": "Berklee Jazz Essentials",
    "description": "A Berklee-inspired jazz curriculum covering shell voicings, guide tones, and ii-V-I mastery.",
    "modules": [
        {
            "title": "Jazz Voicings Foundation",
            "theme": "jazz_voicings",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["Shell Voicings (A & B Forms)", "Rootless Voicings", "Voice Leading"],
            "lessons": [
                {
                    "title": "Shell Voicings: Root-3rd-7th",
                    "week_number": 1,
                    "concepts": ["Shell Voicings", "A Form (R-3-7)", "B Form (R-7-3)"],
                    "exercises": [
                        {
                            "title": "ii-V-I Shells Through All Keys",
                            "exercise_type": "voicing",
                            "content": {"pattern": "ii-V-I Cycle", "voicing_type": "shell"},
                            "difficulty": "intermediate"
                        }
                    ]
                },
                {
                    "title": "Rootless Voicings",
                    "week_number": 2,
                    "concepts": ["Type A Rootless", "Type B Rootless", "Tensions"],
                    "exercises": [
                        {
                            "title": "Rootless ii-V-I",
                            "exercise_type": "voicing",
                            "difficulty": "advanced"
                        }
                    ]
                }
            ]
        },
        {
            "title": "Jazz Standards & Improvisation",
            "theme": "jazz_standards",
            "start_week": 5,
            "end_week": 10,
            "outcomes": ["Standard Repertoire", "Chord Tone Soloing", "Approach Notes"],
            "lessons": [
                {
                    "title": "Your First Jazz Standard: Autumn Leaves",
                    "week_number": 5,
                    "concepts": ["ii-V-I Major", "ii-V-i Minor", "Form (AABA)"],
                    "exercises": [
                        {
                            "title": "Autumn Leaves Head",
                            "exercise_type": "repertoire",
                            "content": {"song": "Autumn Leaves", "key": "Gm"},
                            "difficulty": "intermediate"
                        }
                    ]
                }
            ]
        }
    ]
}

CLASSICAL_ABRSM = {
    "title": "Classical Piano: ABRSM Grades 1-3",
    "description": "A structured classical piano curriculum inspired by ABRSM grading.",
    "modules": [
        {
            "title": "Grade 1: Foundations",
            "theme": "classical_grade1",
            "start_week": 1,
            "end_week": 5,
            "outcomes": ["C & G Major Scales", "Basic Arpeggios", "Simple Repertoire"],
            "lessons": [
                {
                    "title": "Scales: C & G Major",
                    "week_number": 1,
                    "concepts": ["Scale Fingering", "Hand Position", "Thumb Under"],
                    "exercises": [
                        {
                            "title": "C Major Scale (2 Octaves)",
                            "exercise_type": "scale",
                            "content": {"scale": "C Major", "octaves": 2},
                            "difficulty": "beginner"
                        }
                    ]
                },
                {
                    "title": "Arpeggios: C & G Major",
                    "week_number": 2,
                    "concepts": ["Arpeggio Fingering", "Wrist Rotation"],
                    "exercises": [
                        {
                            "title": "C Major Arpeggio (2 Octaves)",
                            "exercise_type": "arpeggio",
                            "difficulty": "beginner"
                        }
                    ]
                }
            ]
        },
        {
            "title": "Grade 2: Expanding Technique",
            "theme": "classical_grade2",
            "start_week": 6,
            "end_week": 10,
            "outcomes": ["D, F, Bb Major Scales", "Am, Dm Scales", "Dynamics & Phrasing"],
            "lessons": [
                {
                    "title": "Minor Scales: A & D Natural Minor",
                    "week_number": 6,
                    "concepts": ["Natural Minor", "Relative Major/Minor"],
                    "exercises": [
                        {
                            "title": "A Natural Minor Scale",
                            "exercise_type": "scale",
                            "difficulty": "intermediate"
                        }
                    ]
                }
            ]
        }
    ]
}

LATIN_RHYTHMS = {
    "title": "Latin Piano Rhythms",
    "description": "Unlock the rhythmic world of Latin piano.",
    "modules": [
        {
            "title": "Bossa Nova Essentials",
            "theme": "latin_bossa",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["Bossa Nova Rhythm", "Chord Voicings", "Bass Patterns"],
            "lessons": [
                {
                    "title": "The Bossa Nova Groove",
                    "week_number": 1,
                    "concepts": ["Syncopation", "Bass + Chord Pattern", "Anticipations"],
                    "exercises": [
                        {
                            "title": "Classic Bossa Pattern in Dm",
                            "exercise_type": "rhythm",
                            "content": {"key": "Dm", "pattern": "Bossa Nova"},
                            "difficulty": "intermediate"
                        }
                    ]
                }
            ]
        },
        {
            "title": "Salsa Montuno",
            "theme": "latin_salsa",
            "start_week": 5,
            "end_week": 8,
            "outcomes": ["2-3 Clave", "Montuno Patterns", "Salsa Harmony"],
            "lessons": [
                {
                    "title": "Understanding Clave",
                    "week_number": 5,
                    "concepts": ["2-3 Clave", "3-2 Clave", "Clave Direction"],
                    "exercises": [
                        {
                            "title": "Clapping Clave Patterns",
                            "exercise_type": "rhythm",
                            "difficulty": "beginner"
                        }
                    ]
                }
            ]
        }
    ]
}

MODERN_RNB_PRODUCER = {
    "title": "Modern R&B Producer Keys",
    "description": "Keyboard techniques for R&B and hip-hop production.",
    "modules": [
        {
            "title": "Lo-Fi & Chill Chords",
            "theme": "rnb_lofi",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["Major 7th Voicings", "9th & 11th Extensions", "Detuned Piano Sound"],
            "lessons": [
                {
                    "title": "Lo-Fi Chord Stacks",
                    "week_number": 1,
                    "concepts": ["Maj7/9 Voicings", "Add9 Chords", "Cluster Voicings"],
                    "exercises": [
                        {
                            "title": "Lo-Fi ii-V-I",
                            "exercise_type": "progression",
                            "content": {"chords": ["Dm9", "G13", "Cmaj9"], "style": "lo-fi"},
                            "difficulty": "intermediate"
                        }
                    ]
                }
            ]
        },
        {
            "title": "Trap Soul Progressions",
            "theme": "rnb_trapsoul",
            "start_week": 5,
            "end_week": 8,
            "outcomes": ["Minor Key Progressions", "808 Bass Awareness", "Melancholic Voicings"],
            "lessons": [
                {
                    "title": "The Trap Soul Sound",
                    "week_number": 5,
                    "concepts": ["i-VI-III-VII", "Minor 9ths", "Sparse Voicings"],
                    "exercises": [
                        {
                            "title": "Classic Trap Soul Progression",
                            "exercise_type": "progression",
                            "content": {
                                "chords": ["Am9", "Fmaj7", "Cmaj7", "G"],
                                "key": "Am"
                            },
                            "difficulty": "intermediate"
                        }
                    ]
                }
            ]
        }
    ]
}

WORSHIP_BAND_READY = {
    "title": "Worship Band Ready",
    "description": "Practical keyboard skills for playing in a worship band.",
    "modules": [
        {
            "title": "Worship Keys Fundamentals",
            "theme": "worship_fundamentals",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["Nashville Number System", "Pad Playing", "Team Dynamics"],
            "lessons": [
                {
                    "title": "The Nashville Number System",
                    "week_number": 1,
                    "concepts": ["Number System", "Transposition", "Chord Charts"],
                    "exercises": [
                        {
                            "title": "1-5-6-4 in Every Key",
                            "exercise_type": "progression",
                            "content": {
                                "roman_numerals": ["I", "V", "vi", "IV"],
                                "practice": "all_keys"
                            },
                            "difficulty": "beginner"
                        }
                    ]
                },
                {
                    "title": "Playing Pads & Textures",
                    "week_number": 2,
                    "concepts": ["Pad Sounds", "Sustained Chords", "Less is More"],
                    "exercises": [
                        {
                            "title": "Whole Note Pad Exercise",
                            "exercise_type": "rhythm",
                            "difficulty": "beginner"
                        }
                    ]
                }
            ]
        },
        {
            "title": "Leading & Dynamics",
            "theme": "worship_leading",
            "start_week": 5,
            "end_week": 8,
            "outcomes": ["Building Dynamics", "Intro/Outro Creation", "Spontaneous Worship"],
            "lessons": [
                {
                    "title": "Building Dynamics",
                    "week_number": 5,
                    "concepts": ["Crescendo", "Register Changes", "Rhythmic Intensity"],
                    "exercises": [
                        {
                            "title": "Dynamic Build Exercise",
                            "exercise_type": "dynamics",
                            "difficulty": "intermediate"
                        }
                    ]
                }
            ]
        }
    ]
}

DEFAULT_CURRICULUMS = {
    "funk_mastery": FUNK_MASTERY,
    "gospel_essentials": GOSPEL_KEYS_ESSENTIALS,
    "jazz_bootcamp": JAZZ_IMPROV_BOOTCAMP,
    "neosoul_mastery": NEO_SOUL_MASTERY,
    "contemporary_worship": CONTEMPORARY_WORSHIP,
    "blues_master": BLUES_MASTER_CLASS,
    "berklee_jazz": BERKLEE_JAZZ_ESSENTIALS,
    "classical_abrsm": CLASSICAL_ABRSM,
    "latin_rhythms": LATIN_RHYTHMS,
    "modern_rnb": MODERN_RNB_PRODUCER,
    "worship_band": WORSHIP_BAND_READY,
}