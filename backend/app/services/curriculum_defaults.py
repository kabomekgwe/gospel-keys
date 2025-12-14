"""Default Curriculum Templates.

Pre-defined curriculums for immediate use without AI generation.
"""

GOSPEL_KEYS_ESSENTIALS = {
    "title": "Gospel Keys Essentials",
    "description": "The definitive start to playing traditional and contemporary gospel. Master the 'church sound' through essential voicings, passing chords, and standard progressions.",
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
                    "description": "Introduction to Major 7, Dominant 7, and Minor 7 chords.",
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
                            "content": {
                                "scale": "C Major",
                                "pattern": "Diatonic 7ths"
                            },
                            "difficulty": "beginner",
                            "estimated_duration_minutes": 10
                        },
                        {
                            "title": "Gospel 2-5-1",
                            "description": "The foundational progression of gospel harmony.",
                            "exercise_type": "progression",
                            "content": {
                                "chords": ["Dm9", "G13", "Cmaj9"],
                                "roman_numerals": ["ii9", "V13", "Imaj9"],
                                "key": "C"
                            },
                            "difficulty": "beginner",
                            "estimated_duration_minutes": 15
                        }
                    ]
                },
                {
                    "title": "The Preacher's Chord",
                    "description": "Mastering the dominant 7#9 chord used for shouts and accents.",
                    "week_number": 2,
                    "concepts": ["Dominant 7#9", "Tritones", "Blues Scale"],
                    "exercises": [
                        {
                            "title": "E7#9 Voicing",
                            "description": "Constructing the 'Hendrix' or 'Preacher' chord.",
                            "exercise_type": "voicing",
                            "content": {
                                "chord": "E7#9",
                                "notes": ["E", "G#", "D", "G"]
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 10
                        },
                        {
                            "title": "Preacher Chords in Cycle",
                            "description": "Moving the #9 chord through the cycle of 4ths.",
                            "exercise_type": "progression",
                            "content": {
                                "chords": ["E7#9", "A7#9", "D7#9", "G7#9"],
                                "key": "C" 
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 15
                        }
                    ]
                }
            ]
        },
        {
            "title": "Gospel Progressions & Movements",
            "description": "Connecting chords with soulful classic movements.",
            "theme": "gospel_progressions",
            "start_week": 5,
            "end_week": 8,
            "outcomes": ["7-3-6 Progression", "Tritone Subs", "Gospel Waltz"],
            "lessons": [
                {
                    "title": "The 7-3-6 Progression",
                    "description": "The classic gospel turnaround to the relative minor.",
                    "week_number": 5,
                    "concepts": ["Secondary Dominants", "Diminished Passing Chords"],
                    "exercises": [
                        {
                            "title": "7-3-6 in Ab",
                            "description": "Gdim7 -> C7alt -> Fm9",
                            "exercise_type": "progression",
                            "content": {
                                "key": "Ab",
                                "chords": ["Gdim7", "C7(b9)", "Fm9"],
                                "roman_numerals": ["vii°7/vi", "V7/vi", "vi7"]
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 20
                        }
                    ]
                },
                {
                    "title": "Walk-ups and Walk-downs",
                    "description": "Bass line movements that drive congregational songs.",
                    "week_number": 6,
                    "concepts": ["Bass Lines", "Slash Chords"],
                    "exercises": [
                        {
                            "title": "The 1 to 4 Walk-up",
                            "description": "C -> C/E -> F",
                            "exercise_type": "progression",
                            "content": {
                                "key": "C",
                                "chords": ["C", "C/E", "F", "F#dim7", "C/G"],
                                "roman_numerals": ["I", "I/3", "IV", "#iv°7", "I/5"]
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 15
                        }
                    ]
                }
            ]
        }
    ]
}

JAZZ_IMPROV_BOOTCAMP = {
    "title": "Jazz Improvisation Bootcamp",
    "description": "A step-by-step roadmap from basic swing to confident soloing. Focuses on 'Shell Voicings', 2-5-1 mastery, and guide tones.",
    "modules": [
        {
            "title": "Jazz Fundamentals",
            "theme": "jazz_basics",
            "start_week": 1,
            "end_week": 4,
            "lessons": [
                {
                    "title": "Shell Voicings (A & B Forms)",
                    "description": "Left hand voicings using Root, 3rd, and 7th.",
                    "week_number": 1,
                    "concepts": ["Shell Voicings", "Voice Leading", "Swing Feel"],
                    "exercises": [
                        {
                            "title": "Shells around the Cycle",
                            "description": "Play ii-V-I shells through all 12 keys.",
                            "exercise_type": "voicing",
                            "content": {
                                "pattern": "ii-V-I Cycle",
                                "voicing_type": "shell"
                            },
                            "difficulty": "beginner",
                            "estimated_duration_minutes": 20
                        }
                    ]
                },
                {
                    "title": "Guide Tone Lines",
                    "description": "Connecting 3rds and 7ths to create smooth melodies.",
                    "week_number": 2,
                    "concepts": ["Guide Tones", "Thirds and Sevenths"],
                    "exercises": [
                        {
                            "title": "Guide Tones on Blue Bossa",
                            "description": "Play only 3rds and 7ths over Blue Bossa changes.",
                            "exercise_type": "progression",
                            "content": {
                                "key": "Cm",
                                "chords": ["Cm7", "Fm7", "Dm7b5", "G7alt"]
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 15
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
                    "description": "Using chord tones (1-3-5-7) to outline changes.",
                    "week_number": 5,
                    "concepts": ["Chord Tones", "Arpeggios"],
                    "exercises": [
                        {
                            "title": "Arpeggios over 2-5-1",
                            "description": "Ascending and descending arpeggios over major 2-5-1s.",
                            "exercise_type": "scale",
                            "content": {
                                "pattern": "1-3-5-7 Up, 7-5-3-1 Down",
                                "key": "Bb"
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 20
                        }
                    ]
                },
                {
                    "title": "Approach Notes",
                    "description": "Adding chromaticism to target notes.",
                    "week_number": 6,
                    "concepts": ["Chromatics", "Enclosures"],
                    "exercises": [
                        {
                            "title": "Half-step Approaches",
                            "description": "Approach every 3rd of a chord from a half-step below.",
                            "exercise_type": "lick",
                            "content": {
                                "pattern": "Chromatic Approach"
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 15
                        }
                    ]
                }
            ]
        }
    ]
}

NEO_SOUL_MASTERY = {
    "title": "Neo-Soul Mastery",
    "description": "Unlock the smooth, laid-back sounds of R&B and Soul. Learn lush extended chords, cluster voicings, and the 'Dilla' groove.",
    "modules": [
        {
            "title": "Neo-Soul Harmony",
            "theme": "neosoul_basics",
            "start_week": 1,
            "end_week": 4,
            "lessons": [
                {
                    "title": "The Minor 11th Chord",
                    "description": "The quintessential Neo-Soul chord.",
                    "week_number": 1,
                    "concepts": ["Minor 9th", "Minor 11th", "Cluster Voicings"],
                    "exercises": [
                        {
                            "title": "Eb Minor 11 Deep Dive",
                            "description": "Voicing Eb-11 with clusters (Root-5-b7 in LH, 9-11-5 in RH).",
                            "exercise_type": "voicing",
                            "content": {
                                "chord": "Ebm11",
                                "notes": ["Eb", "Bb", "Db", "F", "Ab", "Bb"]
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 15
                        }
                    ]
                },
                {
                    "title": "Tritone Substitution",
                    "description": "Reharmonizing V chords for smooth chromatic bass movement.",
                    "week_number": 2,
                    "exercises": [
                        {
                            "title": "Tritone Subs in 2-5-1",
                            "description": "Replacing G7 with Db7 in a C major 2-5-1.",
                            "exercise_type": "progression",
                            "content": {
                                "chords": ["Dm9", "Db9#11", "Cmaj9"],
                                "roman_numerals": ["ii9", "subV7", "Imaj9"]
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 20
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
                    "description": "Playing behind the beat for that drunken drum feel.",
                    "week_number": 5,
                    "concepts": ["Micro-timing", "Syncopation"],
                    "exercises": [
                        {
                            "title": "Laid Back Scales",
                            "description": "Playing major scales with a heavy swing/lag.",
                            "exercise_type": "rhythm",
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 15
                        }
                    ]
                },
                {
                    "title": "Grace Notes & Slides",
                    "description": "Decorating simpler chords to make them soulful.",
                    "week_number": 6,
                    "concepts": ["Pentatonic Slides", "Crushed Notes"],
                    "exercises": [
                        {
                            "title": "Pentatonic Grace Notes",
                            "description": "Sliding from b3 to 3 over major chords.",
                            "exercise_type": "lick",
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 10
                        }
                    ]
                }
            ]
        }
    ]
}

CONTEMPORARY_WORSHIP = {
    "title": "Contemporary Worship Piano",
    "description": "Modern techniques for P&W music. Focus on Sus chords, pads, textures, and the 1-5-6-4 progression.",
    "modules": [
        {
            "title": "Worship Essentials",
            "theme": "worship_basics",
            "start_week": 1,
            "end_week": 4,
            "lessons": [
                {
                    "title": "Suspended Chords (Sus2 & Sus4)",
                    "description": "Creating open, airy textures.",
                    "week_number": 1,
                    "concepts": ["Sus2", "Sus4", "Add2"],
                    "exercises": [
                        {
                            "title": "Sus Chords in D Major",
                            "description": "Alternating D and Dsus4, A and Asus4.",
                            "exercise_type": "voicing",
                            "content": {
                                "key": "D",
                                "chords": ["Dsus4", "D", "Asus4", "A"]
                            },
                            "difficulty": "beginner",
                            "estimated_duration_minutes": 10
                        }
                    ]
                },
                {
                    "title": "Slash Chords",
                    "description": "Creating movement over static bass lines.",
                    "week_number": 2,
                    "exercises": [
                        {
                            "title": "1 over 5 Slash Chords",
                            "description": "Playing C/G, F/C for smooth voice leading.",
                            "exercise_type": "progression",
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 15
                        }
                    ]
                }
            ]
        }
    ]
}

DEFAULT_CURRICULUMS = {
    "gospel_essentials": GOSPEL_KEYS_ESSENTIALS,
    "jazz_bootcamp": JAZZ_IMPROV_BOOTCAMP,
    "neosoul_mastery": NEO_SOUL_MASTERY,
    "contemporary_worship": CONTEMPORARY_WORSHIP,
}
