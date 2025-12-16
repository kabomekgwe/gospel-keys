"""
MULTI - LEVEL PIANO MASTERY SYSTEM
Complete curriculum templates for 4 skill levels across 8 major genres
"""

# ============================================================================
# UNIVERSAL SKILL LEVEL DEFINITIONS
# ============================================================================

SKILL_LEVEL_DEFINITIONS = {
    "beginner": {
        "description": "0-2 years experience, basic note reading, simple rhythms",
        "technical_benchmarks": {
            "scales": "Major scales 1 octave, 60 BPM",
            "arpeggios": "Simple triads, hands separate",
            "chords": "Major/minor triads in root position",
            "reading": "Simple melodies with chord symbols",
            "repertoire": "1-2 page pieces, slow tempo"
        },
        "practice_time": "15-30 minutes daily, 3-5 days/week",
        "assessment_criteria": "Accuracy over speed, basic musicality"
    },

    "intermediate": {
        "description": "2-5 years experience, comfortable with key signatures, basic improvisation",
        "technical_benchmarks": {
            "scales": "All major/minor scales 2 octaves, 100 BPM",
            "arpeggios": "Triads and 7th chords, hands together",
            "chords": "7th chords in inversions, basic voicings",
            "reading": "Intermediate pieces with expression marks",
            "repertoire": "3-5 page pieces, moderate tempo",
            "improvisation": "Simple patterns over chord progressions"
        },
        "practice_time": "45-60 minutes daily, 5-6 days/week",
        "assessment_criteria": "Technical control, musical expression, stylistic awareness"
    },

    "advanced": {
        "description": "5-10 years experience, advanced technique, strong theoretical knowledge",
        "technical_benchmarks": {
            "scales": "All scales 4 octaves, 144 BPM, in thirds/sixths",
            "arpeggios": "All inversions, extended chords, 120 BPM",
            "chords": "Advanced voicings, upper structures, reharmonization",
            "reading": "Advanced literature, orchestral reductions",
            "repertoire": "Complete sonatas, concertos, 10+ page works",
            "improvisation": "Sophisticated solos over complex changes",
            "accompaniment": "Professional-level accompanying skills"
        },
        "practice_time": "90-120 minutes daily, 6-7 days/week",
        "assessment_criteria": "Artistic interpretation, technical mastery, creative voice"
    },

    "master": {
        "description": "10+ years experience, professional performance level, teaching ability",
        "technical_benchmarks": {
            "scales": "Any scale pattern on demand, extreme tempos, perfect control",
            "arpeggios": "Complete mastery, any inversion/pattern at tempo",
            "chords": "Instant recognition/execution of any chord in any voicing",
            "reading": "Sight-read advanced literature at performance level",
            "repertoire": "Extensive repertoire across multiple genres/styles",
            "improvisation": "Personal language, advanced concepts, composition",
            "accompaniment": "Conducting, arranging, production skills"
        },
        "practice_time": "3+ hours daily (structured practice)",
        "assessment_criteria": "Artistic contribution, teaching ability, professional recognition"
    }
}

# ============================================================================
# GOSPEL PIANO COMPLETE SYSTEM(4 Levels)
# ============================================================================

GOSPEL_COMPLETE_SYSTEM = {
    "genre": "gospel",
    "style_variants": ["traditional", "contemporary", "urban", "choir", "solo"],

    "beginner": {
        "title": "Gospel Foundations: Your First Year",
        "duration_weeks": 52,
        "weekly_hours": 3,
        "prerequisites": ["Can read simple music", "Basic major/minor chords"],

        "modules": [
            {
                "title": "Months 1-3: Gospel Basics",
                "lessons": [
                    {
                        "week": 1,
                        "title": "The Gospel Sound: Major & Minor Chords",
                        "focus": "Basic chord quality recognition and playing",
                        "technical_work": {
                            "chords": [
                                { "type": "C Major", "voicing": "root position", "hands": "together" },
                                { "type": "F Major", "voicing": "root position", "hands": "together" },
                                { "type": "G Major", "voicing": "root position", "hands": "together" }
                            ],
                            "practice_routine": "5 minutes each chord, focus on even tone"
                        },
                        "rhythmic_foundation": {
                            "pattern": "Quarter note chords on beats 2 and 4",
                            "metronome_start": 60,
                            "metronome_target": 80
                        },
                        "repertoire": {
                            "piece": "Simple hymn: 'Amazing Grace'",
                            "chords_used": ["C", "F", "G"],
                            "rhythm": "Basic quarter notes",
                            "performance_goal": "Play with steady rhythm, correct notes"
                        },
                        "ear_training": "Identify major vs minor chords",
                        "creative_task": "Create simple 4-chord progression"
                    },
                    {
                        "week": 2,
                        "title": "Adding the 7th: Gospel Color",
                        "focus": "Dominant 7th chords and basic voice leading",
                        "technical_work": {
                            "chords": [
                                { "type": "C7", "notes": "C-E-G-Bb", "fingering": "1-2-3-5" },
                                { "type": "F7", "notes": "F-A-C-Eb", "fingering": "1-2-4-5" },
                                { "type": "G7", "notes": "G-B-D-F", "fingering": "1-2-3-5" }
                            ],
                            "practice_routine": "Play around circle of 4ths: C7-F7-Bb7-Eb7..."
                        },
                        "progression_study": {
                            "name": "Gospel 1-4-5 with 7ths",
                            "chords": ["C7", "F7", "G7", "C7"],
                            "voicing": "Root position, close voicing",
                            "practice_tempo": "60-80 BPM"
                        },
                        "improvisation_intro": {
                            "scale": "C Major Pentatonic",
                            "notes": "C-D-E-G-A",
                            "pattern": "Simple 4-note patterns over C7"
                        }
                    }
                ],
                "assessment": {
                    "technical": "Play C, F, G, Am chords with correct fingering",
                    "rhythmic": "Maintain steady beat at 80 BPM",
                    "repertoire": "Perform 'Amazing Grace' with basic gospel feel",
                    "theoretical": "Identify chord types by ear"
                }
            },

            {
                "title": "Months 4-6: Basic Progressions & Feel",
                "lessons": [
                    {
                        "week": 13,
                        "title": "The 2-5-1 Gospel Progression",
                        "focus": "Fundamental progression mastery",
                        "progression_breakdown": {
                            "in_C": {
                                "ii": "Dm7 (D-F-A-C)",
                                "V": "G7 (G-B-D-F)",
                                "I": "Cmaj7 (C-E-G-B)"
                            },
                            "practice_methods": [
                                "Play as block chords",
                                "Play as broken chords (arpeggiated)",
                                "Play with basic gospel rhythm"
                            ],
                            "transposition": "Practice in F and G keys"
                        },
                        "voice_leading_intro": {
                            "concept": "Common tones and stepwise motion",
                            "example": "From Dm7 to G7: Keep F, move D→C, A→B",
                            "exercise": "Practice smooth transitions between chords"
                        }
                    }
                ]
            }
        ],

        "final_project": {
            "title": "Play a Complete Gospel Song",
            "requirements": [
                "3-4 minute performance",
                "Use at least 3 different chord types",
                "Incorporate basic gospel rhythm",
                "Include simple improvisation section",
                "Record with backing track"
            ]
        }
    },

    "intermediate": {
        "title": "Gospel Development: Building Your Vocabulary",
        "duration_weeks": 52,
        "weekly_hours": 6,
        "prerequisites": ["Complete beginner level", "All major/minor scales", "Basic 7th chords"],

        "modules": [
            {
                "title": "Months 1-3: Advanced Gospel Harmony",
                "lessons": [
                    {
                        "week": 1,
                        "title": "9th, 11th, 13th Chords: The Gospel Palette",
                        "focus": "Extended chord construction and application",
                        "chord_family_study": {
                            "major_9": {
                                "construction": "1-3-5-7-9",
                                "example_C": "C-E-G-B-D",
                                "voicings": ["Close position", "Drop 2", "Spread voicing"],
                                "usage": "Tonic function, lush sound"
                            },
                            "dominant_13": {
                                "construction": "1-3-5-b7-9-13",
                                "example_G": "G-B-D-F-A-E",
                                "voicings": ["Shell + extensions", "Quartal voicing"],
                                "usage": "V chord with maximum tension"
                            },
                            "minor_11": {
                                "construction": "1-b3-5-b7-9-11",
                                "example_Dm": "D-F-A-C-E-G",
                                "voicings": ["Cluster voicing", "Open position"],
                                "usage": "Minor tonic, neo-soul sound"
                            }
                        },
                        "exercises": [
                            {
                                "type": "Chord Construction Drill",
                                "task": "Build each extended chord type in all 12 keys",
                                "tempo": "60 BPM, 2 beats per chord",
                                "success_criteria": "100% accuracy, smooth transitions"
                            },
                            {
                                "type": "Progression Application",
                                "task": "Play 2-5-1 with extended chords",
                                "example": "Dm9 - G13 - Cmaj9",
                                "focus": "Voice leading with extensions"
                            }
                        ]
                    },
                    {
                        "week": 2,
                        "title": "Passing Chords & Chromatic Movement",
                        "focus": "Connecting chords with gospel flavor",
                        "techniques": [
                            {
                                "name": "Diminished Passing Chords",
                                "application": "Between chords a whole step apart",
                                "example": "C → C#dim7 → Dm7",
                                "theory": "Dim7 chords divide octave equally"
                            },
                            {
                                "name": "Secondary Dominants",
                                "application": "Temporary V chords for color",
                                "example": "In C: A7 before Dm7 (V7/ii)",
                                "function": "Creates stronger pull to target chord"
                            }
                        ],
                        "exercise_sequence": {
                            "level_1": "Add one passing chord to basic progression",
                            "level_2": "Create chain of passing chords",
                            "level_3": "Improvise passing chord choices in real time"
                        }
                    }
                ]
            },

            {
                "title": "Months 4-6: Gospel Rhythm Mastery",
                "lessons": [
                    {
                        "week": 13,
                        "title": "Shuffle, Swing, and Gospel Grooves",
                        "focus": "Authentic rhythmic feels",
                        "groove_study": {
                            "traditional_shuffle": {
                                "description": "Triplet-based feel with emphasis on 2 and 4",
                                "left_hand": "Root-fifth octave pattern",
                                "right_hand": "Chord stabs on offbeats",
                                "tempo_range": "80-120 BPM",
                                "reference_tracks": ["Mahalia Jackson", "Shirley Caesar"]
                            },
                            "contemporary_gospel": {
                                "description": "Straight 8ths with hip-hop influence",
                                "left_hand": "Simpler patterns, more space",
                                "right_hand": "Rhythmic chord hits, fills",
                                "tempo_range": "70-100 BPM",
                                "reference_tracks": ["Kirk Franklin", "Tasha Cobbs"]
                            }
                        },
                        "independence_exercises": [
                            {
                                "title": "2 vs 3 Polyrhythm",
                                "description": "LH plays duple, RH plays triple feel",
                                "practice_method": "Start slow, use metronome subdivision",
                                "application": "Creates rhythmic tension in ballads"
                            }
                        ]
                    }
                ]
            }
        ],

        "final_project": {
            "title": "Arrange and Perform Gospel Standard",
            "requirements": [
                "5-minute arrangement of traditional gospel song",
                "Include intro, verses, chorus, bridge, ending",
                "Use extended chords and passing chords",
                "Demonstrate multiple gospel rhythms",
                "Include improvisation section",
                "Record with professional quality"
            ]
        }
    },

    "advanced": {
        "title": "Gospel Artistry: Developing Your Voice",
        "duration_weeks": 52,
        "weekly_hours": 10,
        "prerequisites": ["Complete intermediate level", "Strong chord vocabulary", "Good rhythmic feel"],

        "modules": [
            {
                "title": "Months 1-3: Advanced Reharmonization",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Tritone Substitution Systems",
                        "focus": "Complete chromatic harmony approach",
                        "theory_deep_dive": {
                            "mathematical_basis": "Dominant chords a tritone apart share 3rd/7th",
                            "voice_leading": "Creates chromatic bass movement",
                            "application_rules": "Can substitute any V7 chord"
                        },
                        "exercise_system": {
                            "level_1": "Basic tritone sub in 2-5-1",
                            "level_2": "Chain substitutions (multiple in row)",
                            "level_3": "Combined with other substitution types",
                            "level_4": "Application to complete songs"
                        },
                        "creative_project": {
                            "title": "Reharmonize 'Great Is Thy Faithfulness'",
                            "requirements": [
                                "Use at least 5 tritone substitutions",
                                "Maintain hymn recognizability",
                                "Create emotional journey through harmony"
                            ]
                        }
                    },
                    {
                        "week": 2,
                        "title": "Modal Interchange & Borrowed Chords",
                        "focus": "Expanding harmonic palette beyond diatonic",
                        "concept": "Borrow chords from parallel modes",
                        "common_borrowings": {
                            "from_parallel_minor": ["bIII", "bVI", "bVII"],
                            "example_in_C": ["Eb", "Ab", "Bb chords"],
                            "emotional_effect": "Adds poignancy, soulfulness"
                        },
                        "application_exercises": [
                            {
                                "task": "Take I-IV-V progression, add borrowed chords",
                                "example": "C - F - G becomes C - Ab - Bb - G",
                                "analysis": "Creates unexpected, emotional movement"
                            }
                        ]
                    }
                ]
            },

            {
                "title": "Months 4-6: Advanced Improvisation",
                "lessons": [
                    {
                        "week": 13,
                        "title": "Melodic Development & Thematic Soloing",
                        "focus": "Creating meaningful improvisations",
                        "development_techniques": [
                            {
                                "name": "Motivic Development",
                                "description": "Take small idea and expand",
                                "methods": ["Sequence", "Inversion", "Augmentation", "Diminution"],
                                "exercise": "Develop 2-bar motif into 16-bar solo"
                            },
                            {
                                "name": "Quoting and Referencing",
                                "description": "Incorporate hymn melodies into solos",
                                "skill": "Seamless integration of familiar material",
                                "exercise": "Improvise solo that quotes 3 different hymns"
                            }
                        ],
                        "solo_structure": {
                            "beginning": "Establish theme, simple statements",
                            "middle": "Development, tension building",
                            "climax": "Highest intensity, technical peak",
                            "resolution": "Return to theme, peaceful ending"
                        }
                    }
                ]
            }
        ],

        "final_project": {
            "title": "Create Original Gospel Composition",
            "requirements": [
                "Original 5-7 minute gospel composition",
                "Full arrangement with intro/outro",
                "Advanced harmonic techniques",
                "Multiple sections with contrast",
                "Professional recording quality",
                "Written score with chord analysis"
            ]
        }
    },

    "master": {
        "title": "Gospel Ministry: Leadership & Innovation",
        "duration_weeks": 52,
        "weekly_hours": 15,
        "prerequisites": ["Complete advanced level", "Performance experience", "Teaching ability"],

        "modules": [
            {
                "title": "Months 1-3: Music Ministry Leadership",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Directing Worship & Choirs",
                        "focus": "Leading musical worship effectively",
                        "skills_developed": [
                            "Service planning and flow",
                            "Rehearsal techniques for different levels",
                            "Communication with pastors and team",
                            "Creating worship atmosphere"
                        ],
                        "practical_components": [
                            {
                                "task": "Plan complete worship service",
                                "elements": ["Song selection", "Key planning", "Transition planning", "Spontaneous worship"]
                            },
                            {
                                "task": "Conduct choir rehearsal",
                                "skills": ["Vocal warmups", "Part teaching", "Blend and balance", "Expression"]
                            }
                        ]
                    },
                    {
                        "week": 2,
                        "title": "Arranging for Gospel Ensemble",
                        "focus": "Creating parts for full band",
                        "instrumentation_study": {
                            "keyboard_parts": ["Piano", "Organ", "Synth pads", "Electric piano"],
                            "rhythm_section": ["Bass lines", "Drum patterns", "Guitar parts"],
                            "horns_strings": ["Brass arrangements", "String pads", "Woodwind lines"],
                            "vocals": ["Lead vocals", "Background vocals", "Choir arrangements"]
                        },
                        "arranging_project": {
                            "title": "Arrange gospel standard for full band",
                            "requirements": [
                                "Create parts for all instruments",
                                "Include dynamic markings",
                                "Notate vocal harmonies",
                                "Prepare rehearsal scores"
                            ]
                        }
                    }
                ]
            },

            {
                "title": "Months 4-6: Recording & Production",
                "lessons": [
                    {
                        "week": 13,
                        "title": "Gospel Recording Techniques",
                        "focus": "Professional studio skills",
                        "topics": [
                            {
                                "name": "Keyboard Sounds for Gospel",
                                "content": ["Hammond B3 techniques", "Rhodes and Wurli settings", "Modern synth sounds", "Acoustic piano miking"]
                            },
                            {
                                "name": "MIDI Production",
                                "content": ["Programming realistic gospel parts", "Humanizing MIDI", "Creating gospel drum patterns", "Bass programming"]
                            },
                            {
                                "name": "Mixing Gospel Music",
                                "content": ["Keyboard balance in mix", "Vocal treatment", "Creating 'live' feel", "Gospel-specific effects"]
                            }
                        ],
                        "recording_project": {
                            "title": "Produce gospel single",
                            "requirements": [
                                "Record all keyboard parts",
                                "Program rhythm section",
                                "Mix and master",
                                "Create radio-ready production"
                            ]
                        }
                    }
                ]
            }
        ],

        "final_project": {
            "title": "Lead Complete Music Ministry",
            "requirements": [
                "Plan and lead 12-week worship series",
                "Recruit and train music team",
                "Produce recording of original music",
                "Present thesis on gospel music development",
                "Teach gospel piano masterclass"
            ]
        }
    }
}

# ============================================================================
# JAZZ PIANO COMPLETE SYSTEM(4 Levels)
# ============================================================================

JAZZ_COMPLETE_SYSTEM = {
    "genre": "jazz",
    "style_variants": ["swing", "bebop", "modal", "fusion", "contemporary"],

    "beginner": {
        "title": "Jazz Fundamentals: First Steps",
        "duration_weeks": 52,
        "weekly_hours": 3,

        "modules": [
            {
                "title": "Months 1-3: Swing Feel & Basic Harmony",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Understanding Swing Rhythm",
                        "focus": "Internalizing the jazz feel",
                        "exercises": [
                            {
                                "name": "Swing Clapping",
                                "description": "Clap swing rhythm (long-short pattern)",
                                "method": "Use metronome on 2 and 4",
                                "tempo": "60-100 BPM"
                            },
                            {
                                "name": "Basic Comping Pattern",
                                "description": "Chord on beats 2 and 4",
                                "chords": "C7, F7, G7",
                                "focus": "Accenting offbeats"
                            }
                        ]
                    },
                    {
                        "week": 2,
                        "title": "Shell Voicings: Left Hand Foundation",
                        "focus": "Basic jazz chord structure",
                        "voicing_types": {
                            "A_form": "Root-3rd-7th (e.g., C-E-Bb for C7)",
                            "B_form": "Root-7th-3rd (e.g., C-Bb-E for C7)"
                        },
                        "progression_practice": {
                            "ii-V-I in C": "Dm7 (D-F-C), G7 (G-F-B), Cmaj7 (C-E-B)",
                            "practice_method": "Cycle through all keys"
                        }
                    }
                ]
            }
        ],

        "final_project": "Play 12-bar blues with basic swing feel"
    },

    "intermediate": {
        "title": "Jazz Language: Building Vocabulary",
        "duration_weeks": 52,
        "weekly_hours": 6,

        "modules": [
            {
                "title": "Months 1-3: Bebop Language",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Bebop Scales & Patterns",
                        "focus": "Essential bebop vocabulary",
                        "scales": {
                            "dominant_bebop": "1-2-3-4-5-6-b7-7",
                            "major_bebop": "1-2-3-4-5-#5-6-7",
                            "practice_methods": ["Up and down", "Patterns", "Through changes"]
                        },
                        "transcription_project": {
                            "artist": "Charlie Parker",
                            "piece": "Blues for Alice excerpt",
                            "task": "Learn 4-bar phrase"
                        }
                    }
                ]
            }
        ],

        "final_project": "Perform jazz standard with improvisation"
    },

    "advanced": {
        "title": "Jazz Artistry: Advanced Concepts",
        "duration_weeks": 52,
        "weekly_hours": 10,

        "modules": [
            {
                "title": "Months 1-3: Modern Harmony",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Upper Structure Triads",
                        "focus": "Complex chord construction",
                        "concepts": {
                            "over_C7": ["D triad = 9, #11, 13", "Eb triad = b9, #9, #11", "F# triad = #9, #11, b13"],
                            "application": "Add color over basic chords",
                            "voicing": "Play triad in right hand over shell in left"
                        }
                    }
                ]
            }
        ],

        "final_project": "Record album of original jazz compositions"
    },

    "master": {
        "title": "Jazz Innovation: Finding Your Voice",
        "duration_weeks": 52,
        "weekly_hours": 15,

        "modules": [
            {
                "title": "Months 1-3: Composition & Arranging",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Large Ensemble Writing",
                        "focus": "Jazz orchestration",
                        "skills": ["Horn arranging", "Rhythm section writing", "Form development", "Counterpoint"]
                    }
                ]
            }
        ],

        "final_project": "Premiere original jazz suite for ensemble"
    }
}

# ============================================================================
# CLASSICAL PIANO COMPLETE SYSTEM(4 Levels)
# ============================================================================

CLASSICAL_COMPLETE_SYSTEM = {
    "genre": "classical",
    "style_periods": ["baroque", "classical", "romantic", "impressionist", "20th_century", "contemporary"],

    "beginner": {
        "title": "Classical Foundations: Proper Technique",
        "duration_weeks": 52,
        "weekly_hours": 3,

        "modules": [
            {
                "title": "Months 1-3: Hand Position & Basic Technique",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Proper Hand Position & Relaxation",
                        "focus": "Foundation of good technique",
                        "exercises": [
                            {
                                "name": "Finger Lifts",
                                "description": "Lift each finger individually while keeping others relaxed",
                                "purpose": "Develop finger independence",
                                "duration": "5 minutes daily"
                            },
                            {
                                "name": "Five-Finger Patterns",
                                "description": "C-D-E-F-G with proper curved fingers",
                                "focus": "Even tone, legato connection",
                                "tempo": "Quarter note = 60"
                            }
                        ],
                        "repertoire": {
                            "piece": "Bach Minuet in G (attributed)",
                            "technical_focus": "Controlled fingers, simple phrasing",
                            "musical_focus": "Dance character, balanced hands"
                        }
                    }
                ]
            }
        ],

        "final_project": "Recital of 3 contrasting beginner pieces"
    },

    "intermediate": {
        "title": "Classical Development: Technical Expansion",
        "duration_weeks": 52,
        "weekly_hours": 6,

        "modules": [
            {
                "title": "Months 1-3: Scale & Arpeggio Mastery",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Four-Octave Scales with Musicality",
                        "focus": "Technical foundation for intermediate repertoire",
                        "scale_system": {
                            "major_scales": "All 12 keys, 4 octaves",
                            "minor_scales": "Harmonic and melodic, 4 octaves",
                            "practice_methods": [
                                "Hands separate with metronome",
                                "Hands together contrary motion",
                                "In thirds and sixths",
                                "With varied articulation"
                            ],
                            "tempo_goals": "Quarter note = 100-120"
                        },
                        "application": {
                            "repertoire_connection": "Identify scales in current pieces",
                            "sight_reading": "Recognize scale patterns quickly"
                        }
                    }
                ]
            }
        ],

        "final_project": "Perform sonatina or equivalent multi-movement work"
    },

    "advanced": {
        "title": "Classical Artistry: Style & Interpretation",
        "duration_weeks": 52,
        "weekly_hours": 10,

        "modules": [
            {
                "title": "Months 1-3: Style Period Mastery",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Baroque Style: Ornamentation & Articulation",
                        "focus": "Authentic performance practice",
                        "baroque_concepts": {
                            "ornamentation": ["Trills", "Mordents", "Turns", "Appoggiaturas"],
                            "articulation": ["Detached vs legato", "Dance rhythms", "Terraced dynamics"],
                            "tempo": "Steady pulse, minimal rubato"
                        },
                        "repertoire_study": {
                            "bach": "Two-Part Invention in C",
                            "focus": "Voice independence, clear articulation",
                            "performance_practice": "Research authentic interpretations"
                        }
                    }
                ]
            }
        ],

        "final_project": "Full recital program spanning multiple style periods"
    },

    "master": {
        "title": "Classical Virtuosity: Performance & Pedagogy",
        "duration_weeks": 52,
        "weekly_hours": 15,

        "modules": [
            {
                "title": "Months 1-3: Concerto Preparation",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Orchestral Collaboration",
                        "focus": "Performing with orchestra",
                        "skills": [
                            "Following conductor",
                            "Balancing with ensemble",
                            "Cadenza preparation",
                            "Stage presence with orchestra"
                        ],
                        "practice_methods": {
                            "with_recording": "Play along with orchestral recordings",
                            "score_study": "Study full orchestral score",
                            "mock_performance": "Perform with second piano reduction"
                        }
                    }
                ]
            }
        ],

        "final_project": "Perform complete concerto with orchestra"
    }
}

# ============================================================================
# NEO - SOUL / R & B COMPLETE SYSTEM(4 Levels)
# ============================================================================

NEO_SOUL_COMPLETE_SYSTEM = {
    "genre": "neo_soul",
    "substyles": ["neo_soul", "r&b", "hip_hop_soul", "alternative_r&b"],

    "beginner": {
        "title": "Neo-Soul Basics: The Groove",
        "duration_weeks": 52,
        "weekly_hours": 3,

        "modules": [
            {
                "title": "Months 1-3: Neo-Soul Chord Vocabulary",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Minor 11th: The Neo-Soul Sound",
                        "focus": "Signature chord of the genre",
                        "chord_study": {
                            "construction": "1-b3-5-b7-9-11",
                            "example_Am11": "A-C-E-G-B-D",
                            "voicing_tips": [
                                "LH: Root-5th-b7th",
                                "RH: 9th-11th-5th (cluster)",
                                "Spacing: Keep notes close for warmth"
                            ],
                            "practice": "Play in all 12 keys, focus on smooth transitions"
                        },
                        "progression_application": {
                            "simple_loop": "Am11 - Dm11",
                            "rhythm": "Laid-back 8th note groove",
                            "feel": "Behind the beat, relaxed"
                        }
                    }
                ]
            }
        ],

        "final_project": "Create neo-soul loop with chords and simple melody"
    },

    "intermediate": {
        "title": "Neo-Soul Development: Harmony & Rhythm",
        "duration_weeks": 52,
        "weekly_hours": 6,

        "modules": [
            {
                "title": "Months 1-3: Advanced Neo-Soul Harmony",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Cluster Voicings & Quartal Harmony",
                        "focus": "Modern harmonic textures",
                        "voicing_types": {
                            "cluster_voicings": "Notes close together (2nds, 4ths)",
                            "example": "For Cmaj7: C-E-G-B becomes C-D-E-G (cluster)",
                            "effect": "Modern, ambiguous sound"
                        },
                        "quartal_study": {
                            "construction": "Chords built in 4ths",
                            "example": "D-G-C-F (all perfect 4ths)",
                            "application": "Over modal vamps, creates open sound"
                        }
                    }
                ]
            }
        ],

        "final_project": "Produce complete neo-soul track"
    },

    "advanced": {
        "title": "Neo-Soul Artistry: Production & Innovation",
        "duration_weeks": 52,
        "weekly_hours": 10,

        "modules": [
            {
                "title": "Months 1-3: Neo-Soul Production Techniques",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Rhodes & Wurlitzer Programming",
                        "focus": "Iconic neo-soul keyboard sounds",
                        "sound_design": {
                            "rhodes": ["Bell-like attack", "Warm decay", "Tremolo/vibrato", "Phaser effects"],
                            "wurlitzer": ["Bark and bite", "Overdrive settings", "EQ shaping", "Stereo widening"]
                        },
                        "performance_techniques": {
                            "rhodes_touch": "Dynamic sensitivity, grace notes",
                            "wurlitzer_aggression": "Attack variations, percussive hits"
                        }
                    }
                ]
            }
        ],

        "final_project": "EP of original neo-soul compositions"
    },

    "master": {
        "title": "Neo-Soul Innovation: Genre Development",
        "duration_weeks": 52,
        "weekly_hours": 15,

        "modules": [
            {
                "title": "Months 1-3: Genre Fusion & Innovation",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Creating New Hybrid Styles",
                        "focus": "Pushing genre boundaries",
                        "fusion_studies": [
                            {
                                "name": "Neo-Soul + Jazz",
                                "elements": ["Neo-soul harmony with jazz improvisation", "Example: Robert Glasper"],
                                "project": "Create fusion piece"
                            },
                            {
                                "name": "Neo-Soul + Electronic",
                                "elements": ["Analog synths with soulful playing", "Example: James Blake"],
                                "project": "Produce electronic soul track"
                            }
                        ]
                    }
                ]
            }
        ],

        "final_project": "Release genre-defining album with tour"
    }
}

# ============================================================================
# CONTEMPORARY WORSHIP COMPLETE SYSTEM(4 Levels)
# ============================================================================

WORSHIP_COMPLETE_SYSTEM = {
    "genre": "contemporary_worship",
    "substyles": ["hillsong", "bethel", "elevation", "passion", "vineyard"],

    "beginner": {
        "title": "Worship Foundations: Basic Service Playing",
        "duration_weeks": 52,
        "weekly_hours": 3,

        "modules": [
            {
                "title": "Months 1-3: Basic Worship Progressions",
                "lessons": [
                    {
                        "week": 1,
                        "title": "The 1-5-6-4 Progression",
                        "focus": "Most common worship progression",
                        "progression_study": {
                            "in_C": "C-G-Am-F",
                            "practice_methods": [
                                "Block chords with steady rhythm",
                                "Arpeggiated patterns",
                                "With simple right hand melody"
                            ],
                            "transposition": "Practice in G, D, A keys"
                        },
                        "worship_application": {
                            "songs_using": ["Oceans", "10,000 Reasons", "Good Good Father"],
                            "practice": "Play along with recordings"
                        }
                    }
                ]
            }
        ],

        "final_project": "Play complete worship song with band track"
    },

    "intermediate": {
        "title": "Worship Development: Team Dynamics",
        "duration_weeks": 52,
        "weekly_hours": 6,

        "modules": [
            {
                "title": "Months 1-3: Nashville Number System",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Instant Transposition with Numbers",
                        "focus": "Essential skill for worship leading",
                        "system_explanation": {
                            "concept": "Chords represented by scale degrees",
                            "example_in_C": "1=C, 2=Dm, 3=Em, 4=F, 5=G, 6=Am, 7=Bdim",
                            "practice": "Take song chart, transpose to 3 different keys"
                        }
                    }
                ]
            }
        ],

        "final_project": "Lead worship for small group"
    },

    "advanced": {
        "title": "Worship Artistry: Creating Atmosphere",
        "duration_weeks": 52,
        "weekly_hours": 10,

        "modules": [
            {
                "title": "Months 1-3: Spontaneous Worship",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Creating Worship Moments",
                        "focus": "Improvised worship leading",
                        "techniques": [
                            {
                                "name": "Vamp Development",
                                "description": "Take simple progression and build intensity",
                                "methods": ["Dynamic growth", "Register expansion", "Rhythmic development"]
                            },
                            {
                                "name": "Scripture Setting",
                                "description": "Create music for spoken word",
                                "approach": ["Atmospheric pads", "Simple melodic motifs", "Dynamic support"]
                            }
                        ]
                    }
                ]
            }
        ],

        "final_project": "Lead worship for congregation of 100+"
    },

    "master": {
        "title": "Worship Leadership: Ministry Development",
        "duration_weeks": 52,
        "weekly_hours": 15,

        "modules": [
            {
                "title": "Months 1-3: Worship Team Development",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Building & Training Teams",
                        "focus": "Leadership beyond playing",
                        "skills": [
                            "Auditioning musicians",
                            "Creating rehearsal plans",
                            "Developing worship leaders",
                            "Mentoring younger musicians"
                        ]
                    }
                ]
            }
        ],

        "final_project": "Develop complete worship ministry program"
    }
}

# ============================================================================
# BLUES PIANO COMPLETE SYSTEM(4 Levels)
# ============================================================================

BLUES_COMPLETE_SYSTEM = {
    "genre": "blues",
    "substyles": ["delta", "chicago", "texas", "boogie_woogie", "jump_blues", "modern_blues"],

    "beginner": {
        "title": "Blues Basics: 12-Bar Foundation",
        "duration_weeks": 52,
        "weekly_hours": 3,

        "modules": [
            {
                "title": "Months 1-3: Basic Blues Form",
                "lessons": [
                    {
                        "week": 1,
                        "title": "12-Bar Blues in C",
                        "focus": "Fundamental blues structure",
                        "form_study": {
                            "bars_1-4": "C7 (I chord)",
                            "bars_5-8": "F7 (IV chord) then C7",
                            "bars_9-12": "G7 (V chord) then C7",
                            "practice": "Play with steady shuffle rhythm"
                        },
                        "left_hand_patterns": [
                            {
                                "name": "Basic Boogie",
                                "pattern": "Root-fifth-octave-fifth",
                                "rhythm": "Steady 8th notes",
                                "tempo": "80 BPM"
                            }
                        ]
                    }
                ]
            }
        ],

        "final_project": "Perform 12-bar blues with basic solo"
    },

    "intermediate": {
        "title": "Blues Development: Licks & Turnarounds",
        "duration_weeks": 52,
        "weekly_hours": 6,

        "modules": [
            {
                "title": "Months 1-3: Classic Blues Licks",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Muddy Waters Vocabulary",
                        "focus": "Chicago blues piano style",
                        "licks": [
                            {
                                "name": "Shuffle Lick 1",
                                "notes": "C-Eb-F-Gb-G-Bb",
                                "rhythm": "Triplet based",
                                "application": "Over C7 chord"
                            }
                        ],
                        "transcription_project": {
                            "artist": "Otis Spann",
                            "song": "Country Girl",
                            "task": "Learn 8-bar piano intro"
                        }
                    }
                ]
            }
        ],

        "final_project": "Perform blues set with multiple styles"
    },

    "advanced": {
        "title": "Blues Artistry: Regional Styles",
        "duration_weeks": 52,
        "weekly_hours": 10,

        "modules": [
            {
                "title": "Months 1-3: Advanced Blues Styles",
                "lessons": [
                    {
                        "week": 1,
                        "title": "New Orleans Piano Tradition",
                        "focus": "Professor Longhair style",
                        "techniques": [
                            {
                                "name": "Rumba Boogie",
                                "description": "Latin-influenced blues",
                                "rhythm": "Clave-based left hand",
                                "right_hand": "Tremolo and trills"
                            }
                        ]
                    }
                ]
            }
        ],

        "final_project": "Record blues album showcasing multiple styles"
    },

    "master": {
        "title": "Blues Mastery: Innovation & Tradition",
        "duration_weeks": 52,
        "weekly_hours": 15,

        "modules": [
            {
                "title": "Months 1-3: Blues Composition & Innovation",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Modern Blues Evolution",
                        "focus": "Pushing blues boundaries",
                        "innovators_study": [
                            {
                                "artist": "Dr. John",
                                "contribution": "Gris-gris, psychedelic blues",
                                "project": "Create modern blues fusion piece"
                            }
                        ]
                    }
                ]
            }
        ],

        "final_project": "Premiere original blues suite"
    }
}

# ============================================================================
# LATIN PIANO COMPLETE SYSTEM(4 Levels)
# ============================================================================

LATIN_COMPLETE_SYSTEM = {
    "genre": "latin",
    "styles": ["bossa_nova", "salsa", "merengue", "bachata", "cuban_son", "afro_cuban"],

    "beginner": {
        "title": "Latin Basics: Bossa Nova & Salsa",
        "duration_weeks": 52,
        "weekly_hours": 3,

        "modules": [
            {
                "title": "Months 1-3: Bossa Nova Foundation",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Bossa Nova Rhythm Pattern",
                        "focus": "Essential Brazilian groove",
                        "left_hand_pattern": {
                            "description": "Root on beat 1, chord on & of 2",
                            "example": "For Dm7: D (beat 1), chord (D-F-A-C on & of 2)",
                            "practice": "Slow with metronome, focus on anticipation"
                        },
                        "right_hand": {
                            "role": "Melody or chord stabs",
                            "rhythm": "Syncopated, complementary to LH"
                        }
                    }
                ]
            }
        ],

        "final_project": "Perform basic bossa nova tune"
    },

    "intermediate": {
        "title": "Latin Development: Clave & Montunos",
        "duration_weeks": 52,
        "weekly_hours": 6,

        "modules": [
            {
                "title": "Months 1-3: Salsa Piano Fundamentals",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Montuno Patterns",
                        "focus": "Driving salsa piano",
                        "pattern_study": {
                            "basic_montuno": "Two-bar repeating pattern",
                            "example": "Over C7: C-E-G (downbeat), Bb-D-F (syncopated)",
                            "clave_alignment": "Pattern must align with clave direction"
                        }
                    }
                ]
            }
        ],

        "final_project": "Play salsa tune with full rhythm section"
    },

    "advanced": {
        "title": "Latin Artistry: Advanced Rhythms",
        "duration_weeks": 52,
        "weekly_hours": 10,

        "modules": [
            {
                "title": "Months 1-3: Afro-Cuban Jazz",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Complex Clave Patterns",
                        "focus": "Advanced rhythmic concepts",
                        "patterns": [
                            {
                                "name": "6/8 Clave",
                                "description": "African-derived 12/8 feel",
                                "application": "Afro-Cuban jazz, religious music"
                            }
                        ]
                    }
                ]
            }
        ],

        "final_project": "Perform complex Latin jazz composition"
    },

    "master": {
        "title": "Latin Mastery: Innovation & Fusion",
        "duration_weeks": 52,
        "weekly_hours": 15,

        "modules": [
            {
                "title": "Months 1-3: Latin Fusion Composition",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Creating New Latin Hybrids",
                        "focus": "Genre fusion and innovation",
                        "fusion_projects": [
                            {
                                "name": "Latin + Electronica",
                                "elements": ["Traditional rhythms with modern production"],
                                "example": "Bossa nova with house beat"
                            }
                        ]
                    }
                ]
            }
        ],

        "final_project": "Release Latin fusion album"
    }
}

# ============================================================================
# POP / ROCK PIANO COMPLETE SYSTEM(4 Levels)
# ============================================================================

POP_ROCK_COMPLETE_SYSTEM = {
    "genre": "pop_rock",
    "subgenres": ["classic_rock", "pop", "alternative", "singer_songwriter", "indie"],

    "beginner": {
        "title": "Pop/Rock Basics: Essential Progressions",
        "duration_weeks": 52,
        "weekly_hours": 3,

        "modules": [
            {
                "title": "Months 1-3: Rock Piano Foundation",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Power Chords & Octaves",
                        "focus": "Basic rock piano techniques",
                        "techniques": [
                            {
                                "name": "Power Chord Rock",
                                "description": "Root-fifth-octave patterns",
                                "example": "C-G-C in left hand",
                                "rhythm": "8th note driving patterns"
                            },
                            {
                                "name": "Rock Ballad Style",
                                "description": "Arpeggiated chords with melody",
                                "application": "Piano ballads, emotional songs"
                            }
                        ]
                    }
                ]
            }
        ],

        "final_project": "Perform rock/pop song with backing track"
    },

    "intermediate": {
        "title": "Pop/Rock Development: Style Versatility",
        "duration_weeks": 52,
        "weekly_hours": 6,

        "modules": [
            {
                "title": "Months 1-3: Classic Rock Styles",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Billy Joel Piano Style",
                        "focus": "Storytelling through piano rock",
                        "techniques": [
                            {
                                "name": "Walking Bass Lines",
                                "description": "Moving bass under chords",
                                "example": "Root-3rd-5th-6th patterns"
                            }
                        ],
                        "transcription_project": {
                            "song": "Piano Man",
                            "focus": "Learn signature intro and style"
                        }
                    }
                ]
            }
        ],

        "final_project": "Perform set of pop/rock covers"
    },

    "advanced": {
        "title": "Pop/Rock Artistry: Studio & Stage",
        "duration_weeks": 52,
        "weekly_hours": 10,

        "modules": [
            {
                "title": "Months 1-3: Keyboard Rig Setup",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Live Performance Rig",
                        "focus": "Professional stage setup",
                        "topics": [
                            "Main vs. secondary keyboards",
                            "Splits and layers",
                            "MIDI controller setup",
                            "Sound selection for songs"
                        ]
                    }
                ]
            }
        ],

        "final_project": "Tour-ready pop/rock set with full rig"
    },

    "master": {
        "title": "Pop/Rock Innovation: Production & Songwriting",
        "duration_weeks": 52,
        "weekly_hours": 15,

        "modules": [
            {
                "title": "Months 1-3: Hit Song Analysis",
                "lessons": [
                    {
                        "week": 1,
                        "title": "Deconstructing Pop Hits",
                        "focus": "What makes songs successful",
                        "analysis_framework": [
                            "Chord progression analysis",
                            "Melodic hook identification",
                            "Arrangement techniques",
                            "Production choices"
                        ]
                    }
                ]
            }
        ],

        "final_project": "Write and produce radio-ready single"
    }
}

# ============================================================================
# CURRICULUM BUILDER & PROGRESSION SYSTEM
# ============================================================================

def build_leveled_curriculum(student_profile, target_genre, target_level):
"""
    Build personalized curriculum based on student profile and goals.

    Args:
student_profile: Dict with student information
target_genre: String genre name
target_level: String level(beginner, intermediate, advanced, master)

Returns:
        Complete curriculum for that genre and level
"""
    
    # Map genre to curriculum system
genre_systems = {
    "gospel": GOSPEL_COMPLETE_SYSTEM,
    "jazz": JAZZ_COMPLETE_SYSTEM,
    "classical": CLASSICAL_COMPLETE_SYSTEM,
    "neo_soul": NEO_SOUL_COMPLETE_SYSTEM,
    "worship": WORSHIP_COMPLETE_SYSTEM,
    "blues": BLUES_COMPLETE_SYSTEM,
    "latin": LATIN_COMPLETE_SYSTEM,
    "pop_rock": POP_ROCK_COMPLETE_SYSTEM
}
    
    # Get the appropriate curriculum
if target_genre not in genre_systems:
        raise ValueError(f"Genre {target_genre} not supported")

genre_system = genre_systems[target_genre]

if target_level not in genre_system:
        raise ValueError(f"Level {target_level} not available for {target_genre}")

curriculum = genre_system[target_level]
    
    # Personalize based on student profile
personalized = personalize_curriculum(curriculum, student_profile)
    
    # Add assessment system
complete = add_assessment_system(personalized)
    
    # Generate practice plan
practice_plan = generate_practice_plan(complete, student_profile)

return {
    "curriculum": complete,
    "practice_plan": practice_plan,
    "milestones": generate_milestones(complete),
    "resources": get_recommended_resources(target_genre, target_level)
}

def personalize_curriculum(curriculum, student_profile):
"""Adapt curriculum to student's specific needs and interests."""

personalized = curriculum.copy()
    
    # Adjust pace based on available practice time
weekly_hours = student_profile.get("weekly_practice_hours",
    curriculum.get("weekly_hours", 3))
    
    # Scale duration based on practice time
base_duration = curriculum.get("duration_weeks", 52)
base_hours = curriculum.get("weekly_hours", 3)

if weekly_hours > 0:
        # Simple scaling: more hours = faster progress
scale_factor = base_hours / weekly_hours
personalized["duration_weeks"] = int(base_duration * scale_factor)
    else:
personalized["duration_weeks"] = base_duration
    
    # Add student - specific goals
if "goals" in student_profile:
    personalized["student_goals"] = student_profile["goals"]
    
    # Adjust final project based on student interests
if "interests" in student_profile:
    interests = student_profile["interests"]
        # Could modify final project to align with interests
    
    return personalized

def generate_practice_plan(curriculum, student_profile):
"""Create detailed weekly practice plan."""

weekly_hours = student_profile.get("weekly_practice_hours",
    curriculum.get("weekly_hours", 3))
    
    # Convert to daily minutes(assuming 5 days / week)
daily_minutes = (weekly_hours * 60) / 5

plan = {
    "weekly_structure": {
        "technical_work": daily_minutes * 0.3,  # 30 %
            "repertoire": daily_minutes * 0.4,      # 40 %
                "improvisation": daily_minutes * 0.2,   # 20 %
                    "theory_ear_training": daily_minutes * 0.1  # 10 %
        },
    "daily_schedule": []
}
    
    # Generate sample week
for day in range(1, 6):  # Monday to Friday
day_plan = {
    "day": day,
    "warmup": {
        "duration": 10,
        "exercises": ["Scales", "Arpeggios", "Chord drills"]
    },
    "main_session": {
        "focus": get_daily_focus(curriculum, day),
        "duration": daily_minutes - 10,
        "exercises": generate_daily_exercises(curriculum, day)
    },
    "cool_down": {
        "duration": 5,
        "activity": "Free play, listening, or review"
    }
}
plan["daily_schedule"].append(day_plan)

return plan

def get_daily_focus(curriculum, day_number):
"""Determine focus for given day of week."""

foci = [
    "Technical development",
    "Repertoire learning",
    "Improvisation skills",
    "Ear training/theory",
    "Performance practice"
]

return foci[(day_number - 1) % len(foci)]

def generate_milestones(curriculum):
"""Create milestone markers throughout curriculum."""

duration = curriculum.get("duration_weeks", 52)
milestones = {}
    
    # Key percentage points
percentages = [0.25, 0.5, 0.75, 1.0]

for perc in percentages:
    week = int(duration * perc)
milestones[f"week_{week}"] = {
    "description": f"{int(perc*100)}% completion milestone",
        "assessment_required": True,
            "celebration_suggestion": "Record progress video"
}

return milestones

def get_recommended_resources(genre, level):
"""Get books, recordings, and tools for genre/level."""

resources = {
    "gospel": {
        "beginner": {
            "books": ["Gospel Piano for Beginners by Mark Harrison"],
            "recordings": ["Mahalia Jackson - The Best Of"],
            "tools": ["iReal Pro app for backing tracks"]
        },
        "intermediate": {
            "books": ["The Gospel Pianist by James Fortune"],
            "recordings": ["Kirk Franklin - The Nu Nation Project"],
            "tools": ["Logic Pro for recording"]
        }
    },
        # Add other genres...
    }

return resources.get(genre, {}).get(level, {})

# ============================================================================
# ASSESSMENT SYSTEM
# ============================================================================

ASSESSMENT_SYSTEM = {
    "formative_assessments": {
        "weekly_checkpoints": {
            "technical": "Record scale/arpeggio exercises",
            "repertoire": "Play current piece section",
            "improvisation": "Improvise over backing track",
            "theory": "Complete quiz or written exercise"
        },
        "feedback_mechanisms": [
            "Self-assessment using rubric",
            "AI analysis of recordings",
            "Peer review in community",
            "Teacher feedback (if available)"
        ]
    },

    "summative_assessments": {
        "module_completion": {
            "requirements": [
                "Complete all exercises",
                "Pass technical assessment",
                "Perform repertoire piece",
                "Submit creative project"
            ],
            "grading_rubric": {
                "technical": ["Accuracy", "Tempo", "Consistency"],
                "musical": ["Phrasing", "Dynamics", "Style"],
                "creative": ["Originality", "Development", "Expression"]
            }
        },
        "level_completion": {
            "requirements": [
                "Complete all modules",
                "Pass final project assessment",
                "Demonstrate comprehensive skills",
                "Show growth from beginning"
            ],
            "certification": "Digital badge and certificate"
        }
    },

    "progress_tracking": {
        "metrics": [
            "Practice time consistency",
            "Exercise completion rate",
            "Assessment scores",
            "Skill level improvements"
        ],
        "visualizations": [
            "Skill radar chart",
            "Progress timeline",
            "Comparison to benchmarks",
            "Predictive completion date"
        ]
    }
}

# ============================================================================
# SAMPLE STUDENT JOURNEY
# ============================================================================

def create_sample_journey():
"""Create example of student progression through levels."""
    
    # Student starting as beginner in gospel
student = {
    "name": "Jamal",
    "starting_level": "beginner",
    "target_genre": "gospel",
    "weekly_practice_hours": 5,
    "goals": ["Play in church", "Accompany choir", "Improvise solos"],
    "timeline_years": 4  # Want to reach advanced level in 4 years
}

journey = {
    "year_1": {
        "level": "beginner",
        "curriculum": build_leveled_curriculum(student, "gospel", "beginner"),
        "milestones": [
            "Month 3: Play first complete hymn",
            "Month 6: Accompany simple choir song",
            "Month 9: Basic improvisation over 2-5-1",
            "Month 12: Perform in church service"
        ]
    },
    "year_2": {
        "level": "intermediate",
        "curriculum": build_leveled_curriculum(student, "gospel", "intermediate"),
        "milestones": [
            "Month 3: Play extended chords fluently",
            "Month 6: Lead worship for small group",
            "Month 9: Arrange gospel standard",
            "Month 12: Record first demo"
        ]
    },
    "year_3": {
        "level": "advanced",
        "curriculum": build_leveled_curriculum(student, "gospel", "advanced"),
        "milestones": [
            "Month 3: Master advanced reharmonization",
            "Month 6: Create original composition",
            "Month 9: Perform solo concert",
            "Month 12: Teach beginner class"
        ]
    },
    "year_4": {
        "level": "master",
        "curriculum": build_leveled_curriculum(student, "gospel", "master"),
        "milestones": [
            "Month 3: Lead music ministry",
            "Month 6: Produce worship album",
            "Month 9: Develop training program",
            "Month 12: Graduate as master pianist"
        ]
    }
}

return journey

# ============================================================================
# IMPLEMENTATION GUIDE
# ============================================================================

"""
IMPLEMENTATION PLAN FOR YOUR APP:

1. DATABASE SCHEMA:
- Students table with profile information
    - Curriculums table with JSON storage of these templates
        - Progress tracking for each student - curriculum
            - Assessment results storage
                - Resource library

2. CURRICULUM ENGINE:
- Load appropriate template based on genre / level
    - Personalize based on student data
        - Generate practice plans dynamically
            - Track completion and progression

3. EXERCISE GENERATOR:
- Use templates to create specific exercises
    - Generate MIDI files for practice
        - Create backing tracks in appropriate style
            - Provide variations based on performance

4. ASSESSMENT SYSTEM:
- Record student performances
    - Analyze against rubrics
        - Provide detailed feedback
            - Track progress over time

5. COMMUNITY FEATURES:
- Peer review of performances
    - Masterclass participation
        - Group challenges
            - Performance opportunities

6. TEACHER DASHBOARD:
- Monitor student progress
    - Provide personalized feedback
        - Adjust curriculum as needed
            - Schedule virtual lessons

TECH STACK RECOMMENDATION:
- Backend: Python / FastAPI, PostgreSQL with JSONB
- Frontend: React / Next.js, React Native for mobile
    - Audio: Web Audio API, Tone.js, MIDI.js
        - AI: TensorFlow.js for performance analysis
            - Storage: S3 for audio recordings, Cloudinary for videos
"""

if __name__ == "__main__":
    # Example usage
student = {
    "name": "Sarah",
    "current_level": "intermediate",
    "target_genre": "jazz",
    "weekly_practice_hours": 8,
    "goals": ["Improvise over standards", "Play in jazz combo", "Understand bebop"],
    "learning_style": "analytical"
}

curriculum = build_leveled_curriculum(
    student_profile = student,
    target_genre = "jazz",
    target_level = "intermediate"
)

print(f"Curriculum created for {student['name']}")
print(f"Title: {curriculum['curriculum']['title']}")
print(f"Duration: {curriculum['curriculum']['duration_weeks']} weeks")
print(f"Weekly commitment: {curriculum['curriculum']['weekly_hours']} hours")
print(f"Final project: {curriculum['curriculum']['final_project']}")
    
    # Show first week practice plan
week1 = curriculum['practice_plan']['daily_schedule'][0]
print(f"\nSample Monday practice:")
print(f"Warmup: {week1['warmup']['exercises']}")
print(f"Main focus: {week1['main_session']['focus']}")