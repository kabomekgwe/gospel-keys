# from claude


"""
Expanded Piano Curriculum System with Cross-Genre Bridges and AI Integration

This system demonstrates five key expansions:
1. New genre curriculums (Bebop, Funk, Stride, etc.)
2. Deepened existing curriculums with more lessons and exercises
3. Cross-curriculum bridge concepts
4. Expanded exercise types (ear training, transcription, reharmonization)
5. AI generation integration points
"""

# ============================================================================
# SECTION 1: NEW EXERCISE TYPES
# ============================================================================
# These new exercise types expand beyond the original set and enable
# more sophisticated learning patterns

EXERCISE_TYPES = {
    # Original types (preserved)
    "scale": "Scale patterns and fingering practice",
    "progression": "Chord progressions and harmonic sequences",
    "voicing": "Specific chord voicings and hand positions",
    "rhythm": "Rhythmic patterns and groove development",
    "lick": "Melodic phrases and vocabulary building",
    "repertoire": "Complete songs or standard tunes",
    "arpeggio": "Arpeggio patterns and techniques",
    "dynamics": "Volume and intensity control",
    
    # New exercise types for comprehensive learning
    "ear_training": "Listening and recognition exercises",
    "transcription": "Learning directly from recordings",
    "reharmonization": "Transforming simple progressions",
    "sight_reading": "Reading skills development",
    "improvisation": "Structured creative exercises",
    "comping": "Accompaniment patterns and interaction",
    "walking_bass": "Left-hand bass line construction",
    "melody_harmonization": "Adding chords to melodies",
    "modal_exploration": "Mode-based improvisation",
    "polyrhythm": "Multiple rhythms simultaneously",
}

# ============================================================================
# SECTION 2: AI GENERATION INTEGRATION POINTS
# ============================================================================
# These fields enable dynamic content generation and personalization

AI_GENERATION_CONFIG = {
    "exercise_generation": {
        "enabled": True,
        "params": {
            "difficulty_range": ["beginner", "intermediate", "advanced", "expert"],
            "duration_range": [5, 60],  # minutes
            "style_adaptation": True,  # Adapt to user's preferred genres
            "weakness_targeting": True,  # Generate based on user struggles
        }
    },
    "progression_generation": {
        "enabled": True,
        "params": {
            "genre_fusion": True,  # Create cross-genre progressions
            "complexity_scaling": True,  # Auto-adjust complexity
            "common_tone_optimization": True,  # Voice leading suggestions
        }
    },
    "lick_variation": {
        "enabled": True,
        "params": {
            "transposition": True,  # Generate in all keys
            "rhythmic_variation": True,  # Create rhythmic variants
            "harmonic_substitution": True,  # Offer reharmonized versions
        }
    },
    "personalized_path": {
        "enabled": True,
        "params": {
            "goal_based_sequencing": True,  # Order by user goals
            "prerequisite_checking": True,  # Ensure proper foundation
            "pace_adjustment": True,  # Speed up/slow down dynamically
        }
    }
}

# ============================================================================
# SECTION 3: CROSS-CURRICULUM BRIDGES
# ============================================================================
# These connections show how concepts transfer between genres, enabling
# students to leverage knowledge from one style to accelerate in another

CURRICULUM_BRIDGES = {
    "gospel_to_jazz": {
        "title": "From Church to Club: Gospel Foundations for Jazz",
        "description": "Gospel and jazz share the same harmonic DNA. This bridge helps gospel players transition their ii-V-I knowledge into jazz contexts.",
        "prerequisite_curriculums": ["gospel_essentials"],
        "target_curriculums": ["jazz_bootcamp", "berklee_jazz"],
        "bridging_concepts": [
            {
                "title": "The ii-V-I Connection",
                "gospel_context": "Dm7-G7-C used in shouts and progressions",
                "jazz_context": "Same progression but with extensions (Dm9-G13-Cmaj9)",
                "transition_exercise": {
                    "title": "From Church to Bebop",
                    "description": "Play gospel ii-V-I, then add 9ths and 13ths gradually",
                    "exercise_type": "progression",
                    "difficulty": "intermediate",
                }
            },
            {
                "title": "Dominant 7#9 in Both Worlds",
                "gospel_context": "The Preacher's Chord (E7#9) for shouts",
                "jazz_context": "Altered dominant in bebop lines",
                "transition_exercise": {
                    "title": "Preacher to Parker",
                    "description": "Use the #9 sound in both gospel shouts and jazz lines",
                    "exercise_type": "lick",
                    "difficulty": "advanced",
                }
            }
        ]
    },
    
    "blues_to_neosoul": {
        "title": "Blues DNA in Neo-Soul",
        "description": "Neo-soul is blues harmony dressed in modern clothes. Learn how the blues scale becomes the pentatonic slides of R&B.",
        "prerequisite_curriculums": ["blues_master"],
        "target_curriculums": ["neosoul_mastery"],
        "bridging_concepts": [
            {
                "title": "Blues Scale to Grace Notes",
                "blues_context": "The blues scale with its b5 blue note",
                "neosoul_context": "Same notes used as grace notes and slides",
                "transition_exercise": {
                    "title": "From Muddy Waters to D'Angelo",
                    "description": "Play blues licks, then convert to neo-soul slides",
                    "exercise_type": "transcription",
                    "difficulty": "intermediate",
                }
            }
        ]
    },
    
    "classical_to_jazz": {
        "title": "Classical Technique for Jazz Freedom",
        "description": "Classical training provides the technical foundation that allows jazz players to execute complex ideas with ease.",
        "prerequisite_curriculums": ["classical_abrsm"],
        "target_curriculums": ["jazz_bootcamp", "bebop_mastery"],
        "bridging_concepts": [
            {
                "title": "Scales to Arpeggios to Jazz Lines",
                "classical_context": "Two-octave scales and arpeggios with proper fingering",
                "jazz_context": "Same patterns form the basis of bebop vocabulary",
                "transition_exercise": {
                    "title": "Bach to Bebop",
                    "description": "Play a Bach invention, then extract its lines as jazz licks",
                    "exercise_type": "transcription",
                    "difficulty": "advanced",
                }
            }
        ]
    },
    
    "worship_to_gospel": {
        "title": "Modern Worship Meets Traditional Gospel",
        "description": "Contemporary worship uses softer versions of gospel harmony. Learn to add gospel intensity to worship progressions.",
        "prerequisite_curriculums": ["contemporary_worship", "worship_band"],
        "target_curriculums": ["gospel_essentials"],
        "bridging_concepts": [
            {
                "title": "Sus Chords to 7th Chords",
                "worship_context": "Open sus2 and sus4 voicings",
                "gospel_context": "Add 7ths and 9ths for gospel intensity",
                "transition_exercise": {
                    "title": "Hillsong to Kirk Franklin",
                    "description": "Take a worship progression and gospelize it",
                    "exercise_type": "reharmonization",
                    "difficulty": "intermediate",
                }
            }
        ]
    },
    
    "latin_to_jazz": {
        "title": "Latin Rhythms in Jazz Context",
        "description": "Latin jazz combines Afro-Cuban rhythms with jazz harmony. Master the fusion that created legendary albums.",
        "prerequisite_curriculums": ["latin_rhythms"],
        "target_curriculums": ["jazz_bootcamp"],
        "bridging_concepts": [
            {
                "title": "Clave Meets Swing",
                "latin_context": "2-3 clave as foundation",
                "jazz_context": "Superimposing clave over jazz changes",
                "transition_exercise": {
                    "title": "Tito Puente Meets Dizzy",
                    "description": "Play a jazz standard with clave rhythm",
                    "exercise_type": "rhythm",
                    "difficulty": "advanced",
                }
            }
        ]
    }
}

# ============================================================================
# SECTION 4: NEW GENRE CURRICULUMS
# ============================================================================
# Adding genres that fill important gaps in the musical spectrum

BEBOP_MASTERY = {
    "title": "Bebop Piano Mastery",
    "description": "Master the lightning-fast lines and sophisticated harmony of bebop. Learn the language of Bird, Bud Powell, and the jazz revolution.",
    "modules": [
        {
            "title": "Bebop Foundations",
            "description": "The harmonic and melodic vocabulary that defines bebop.",
            "theme": "bebop_basics",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["Bebop Scales", "Chromatic Approach Notes", "Fast Tempos"],
            "lessons": [
                {
                    "title": "The Bebop Scale",
                    "description": "Adding a chromatic passing tone to create even eighth notes over dominant chords.",
                    "week_number": 1,
                    "concepts": ["Bebop Dominant Scale", "Chromatic Passing Tones", "Target Notes"],
                    "theory_content": {
                        "summary": "The bebop scale adds a chromatic note to the mixolydian mode, allowing chord tones to land on downbeats.",
                        "key_points": [
                            "Add a natural 7 to the mixolydian mode (R-2-3-4-5-6-b7-7-R)",
                            "This creates 8 notes, perfect for swinging eighth notes",
                            "Chord tones naturally fall on strong beats"
                        ]
                    },
                    "exercises": [
                        {
                            "title": "G7 Bebop Scale",
                            "description": "G-A-B-C-D-E-F-F#-G over G7 chord.",
                            "exercise_type": "scale",
                            "content": {
                                "scale": "G Bebop Dominant",
                                "notes": ["G", "A", "B", "C", "D", "E", "F", "F#", "G"]
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 15
                        },
                        {
                            "title": "Bebop Scale Over ii-V-I",
                            "description": "Apply bebop scales to the standard jazz progression.",
                            "exercise_type": "improvisation",
                            "content": {
                                "chords": ["Dm7", "G7", "Cmaj7"],
                                "scales": ["D Dorian", "G Bebop Dominant", "C Major"]
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 20
                        }
                    ]
                },
                {
                    "title": "Chromatic Enclosures",
                    "description": "Approaching target notes from above and below for that bebop sound.",
                    "week_number": 2,
                    "concepts": ["Enclosures", "Target Notes", "Chromaticism"],
                    "theory_content": {
                        "summary": "Bebop players surround important chord tones with chromatic approach notes from above and below.",
                        "key_points": [
                            "Approach from half-step above and below simultaneously",
                            "Creates tension and resolution",
                            "Makes simple arpeggios sound sophisticated"
                        ]
                    },
                    "exercises": [
                        {
                            "title": "Enclosing Chord Tones",
                            "description": "Practice approaching the 3rd of each chord with enclosures.",
                            "exercise_type": "lick",
                            "content": {
                                "pattern": "Chromatic Enclosure",
                                "target_notes": "3rds of each chord"
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 20
                        }
                    ]
                },
                {
                    "title": "Digital Patterns",
                    "description": "The systematic note patterns that create bebop's distinctive sound.",
                    "week_number": 3,
                    "concepts": ["1235 Pattern", "1237 Pattern", "Melodic Cells"],
                    "theory_content": {
                        "summary": "Bebop players used short melodic cells or 'digital patterns' that could be sequenced through chord changes.",
                        "key_points": [
                            "1-2-3-5 is the most common bebop pattern",
                            "These patterns can be applied to any chord",
                            "Practice them in all keys for fluency"
                        ]
                    },
                    "exercises": [
                        {
                            "title": "1235 Through ii-V-I",
                            "description": "Play the 1-2-3-5 pattern over Dm7-G7-Cmaj7.",
                            "exercise_type": "lick",
                            "content": {
                                "pattern": "1235",
                                "progression": ["Dm7", "G7", "Cmaj7"]
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 25
                        }
                    ]
                },
                {
                    "title": "Bebop Articulation",
                    "description": "The accents and articulation that make bebop swing hard.",
                    "week_number": 4,
                    "concepts": ["Upbeat Accents", "Ghosting", "Staccato vs Legato"],
                    "exercises": [
                        {
                            "title": "Accent Pattern Practice",
                            "description": "Play scales with bebop accents: strong on 2 and 4.",
                            "exercise_type": "rhythm",
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 15
                        }
                    ]
                }
            ]
        },
        {
            "title": "Bebop Repertoire",
            "description": "Learning the classic bebop heads and their unique challenges.",
            "theme": "bebop_standards",
            "start_week": 5,
            "end_week": 8,
            "outcomes": ["Bebop Heads", "Rhythm Changes", "Fast Tempos"],
            "lessons": [
                {
                    "title": "Donna Lee",
                    "description": "Charlie Parker's iconic bebop line transcribed for piano.",
                    "week_number": 5,
                    "concepts": ["Contrafact", "Bebop Lines", "Fast Passages"],
                    "exercises": [
                        {
                            "title": "Donna Lee Head",
                            "description": "Learn the melody hands together at slow tempo first.",
                            "exercise_type": "transcription",
                            "content": {
                                "song": "Donna Lee",
                                "artist": "Charlie Parker",
                                "tempo_start": 100,
                                "tempo_target": 200
                            },
                            "difficulty": "expert",
                            "estimated_duration_minutes": 45
                        }
                    ]
                }
            ]
        }
    ]
}

STRIDE_PIANO = {
    "title": "Stride Piano Essentials",
    "description": "Master the orchestral left-hand technique of Harlem stride piano. Learn the foundations laid by James P. Johnson, Fats Waller, and Art Tatum.",
    "modules": [
        {
            "title": "Stride Left Hand",
            "description": "Building the alternating bass that defines stride piano.",
            "theme": "stride_basics",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["Oom-Pah Pattern", "Tenths", "Left Hand Independence"],
            "lessons": [
                {
                    "title": "The Basic Stride",
                    "description": "Root on 1 and 3, chord on 2 and 4 - the engine of stride piano.",
                    "week_number": 1,
                    "concepts": ["Bass-Chord Alternation", "Tenths", "Stride Rhythm"],
                    "theory_content": {
                        "summary": "Stride piano creates a full orchestral sound with the left hand alternating between bass notes and chords.",
                        "key_points": [
                            "Low bass note (root or fifth) on beats 1 and 3",
                            "Mid-range chord on beats 2 and 4",
                            "Creates self-contained accompaniment"
                        ]
                    },
                    "exercises": [
                        {
                            "title": "Basic Stride in C",
                            "description": "C bass note, then C-E-G chord, alternating steadily.",
                            "exercise_type": "rhythm",
                            "content": {
                                "key": "C",
                                "pattern": "Basic Stride",
                                "tempo": 120
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 20
                        },
                        {
                            "title": "Stride Around the Cycle",
                            "description": "Practice stride pattern through cycle of fifths.",
                            "exercise_type": "progression",
                            "content": {
                                "pattern": "Stride through keys",
                                "progression": "Cycle of 5ths"
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 30
                        }
                    ]
                },
                {
                    "title": "Playing Tenths",
                    "description": "Stretching the left hand to play root and tenth simultaneously.",
                    "week_number": 2,
                    "concepts": ["Tenth Intervals", "Hand Stretching", "Wrist Rotation"],
                    "theory_content": {
                        "summary": "Stride pianists often play tenths (an octave plus a third) in the left hand to create a fuller bass sound.",
                        "key_points": [
                            "Requires flexible hand position",
                            "Use wrist rotation, not just finger stretch",
                            "Start with smaller intervals if tenths are difficult"
                        ]
                    },
                    "exercises": [
                        {
                            "title": "Tenth Exercises",
                            "description": "Practice C-E, then E-G#, building hand flexibility.",
                            "exercise_type": "scale",
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 15
                        }
                    ]
                }
            ]
        }
    ]
}

FUNK_PIANO = {
    "title": "Funk Piano Fundamentals",
    "description": "Master the syncopated, groove-heavy piano of funk. Learn the vocabulary of Herbie Hancock, George Duke, and Bernie Worrell.",
    "modules": [
        {
            "title": "Funk Rhythms & Comping",
            "description": "The tight, syncopated rhythms that make funk groove.",
            "theme": "funk_basics",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["Syncopated Rhythms", "Stab Patterns", "Bubble Rhythm"],
            "lessons": [
                {
                    "title": "The Funk Bubble",
                    "description": "The bouncing 16th note pattern that drives funk piano.",
                    "week_number": 1,
                    "concepts": ["16th Note Syncopation", "Dead Notes", "Rhythmic Precision"],
                    "theory_content": {
                        "summary": "Funk piano relies on precise 16th note rhythms with ghosted or 'dead' notes creating the groove.",
                        "key_points": [
                            "Play some notes percussively without tone",
                            "Sync perfectly with the drummer's hi-hat",
                            "Less is more - space creates groove"
                        ]
                    },
                    "exercises": [
                        {
                            "title": "Basic Bubble Rhythm in Em",
                            "description": "Play Em7 with the classic bubble pattern.",
                            "exercise_type": "rhythm",
                            "content": {
                                "chord": "Em7",
                                "pattern": "Funk Bubble",
                                "tempo": 95
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 20
                        }
                    ]
                },
                {
                    "title": "Funk Voicings",
                    "description": "The cluster voicings and stacked fourths of funk harmony.",
                    "week_number": 2,
                    "concepts": ["Quartal Harmony", "Cluster Voicings", "Sus Chords"],
                    "theory_content": {
                        "summary": "Funk piano uses voicings built from fourths rather than thirds, creating an open, modal sound.",
                        "key_points": [
                            "Stack perfect fourths: E-A-D or D-G-C",
                            "Often omit the 3rd for ambiguity",
                            "Use the whole piano - spread out voicings"
                        ]
                    },
                    "exercises": [
                        {
                            "title": "Quartal Voicings",
                            "description": "Build voicings from stacked fourths over a funk groove.",
                            "exercise_type": "voicing",
                            "content": {
                                "voicing_type": "quartal",
                                "chords": ["Em7", "Am7", "Dm7"]
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 25
                        }
                    ]
                }
            ]
        }
    ]
}

COUNTRY_HONKYTONK = {
    "title": "Country & Honky-Tonk Piano",
    "description": "Master the rollicking piano styles of country music from Floyd Cramer's slip-note technique to modern Nashville session playing.",
    "modules": [
        {
            "title": "Honky-Tonk Foundations",
            "description": "The driving rhythms and signature techniques of country piano.",
            "theme": "country_basics",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["Slip-Note Technique", "Train Beat", "Country Licks"],
            "lessons": [
                {
                    "title": "The Slip-Note Technique",
                    "description": "Floyd Cramer's iconic grace note approach that defined country piano.",
                    "week_number": 1,
                    "concepts": ["Grace Notes", "Slide Technique", "Country Phrasing"],
                    "theory_content": {
                        "summary": "The slip-note technique involves sliding from a note a half-step below the target note, creating the crying quality of country piano.",
                        "key_points": [
                            "Slide quickly from b3 to 3 for major chords",
                            "Slide from b7 to root for resolution",
                            "Keep the slide quick and crisp"
                        ]
                    },
                    "exercises": [
                        {
                            "title": "Basic Slip-Notes in G",
                            "description": "Practice sliding Bb to B over G major chord.",
                            "exercise_type": "lick",
                            "content": {
                                "key": "G",
                                "technique": "Slip-note"
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

MODAL_JAZZ = {
    "title": "Modal Jazz Exploration",
    "description": "Move beyond chord changes into the open, meditative world of modal jazz. Learn the approaches of McCoy Tyner, Bill Evans, and Herbie Hancock.",
    "modules": [
        {
            "title": "Modal Foundations",
            "description": "Understanding modes and how they create color and mood.",
            "theme": "modal_basics",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["Seven Modes", "Quartal Voicings", "Pedal Points"],
            "lessons": [
                {
                    "title": "The Seven Modes",
                    "description": "Beyond major and minor: exploring Dorian, Phrygian, Lydian, and more.",
                    "week_number": 1,
                    "concepts": ["Modes", "Modal Colors", "Characteristic Notes"],
                    "theory_content": {
                        "summary": "Each mode of the major scale has its own emotional quality and characteristic notes that define its sound.",
                        "key_points": [
                            "Dorian: minor with raised 6th (bright minor)",
                            "Phrygian: minor with lowered 2nd (Spanish/dark)",
                            "Lydian: major with raised 4th (bright/dreamy)",
                            "Mixolydian: major with lowered 7th (bluesy)"
                        ]
                    },
                    "exercises": [
                        {
                            "title": "Modal Colors Exercise",
                            "description": "Play each mode focusing on its characteristic note.",
                            "exercise_type": "modal_exploration",
                            "content": {
                                "modes": ["Dorian", "Phrygian", "Lydian", "Mixolydian"],
                                "focus": "Characteristic notes"
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 25
                        }
                    ]
                },
                {
                    "title": "McCoy Tyner Voicings",
                    "description": "The powerful quartal voicings that revolutionized modal jazz.",
                    "week_number": 2,
                    "concepts": ["Quartal Harmony", "Fourths", "Open Voicings"],
                    "theory_content": {
                        "summary": "McCoy Tyner built chords from stacked perfect fourths, creating a powerful, open sound perfect for modal playing.",
                        "key_points": [
                            "Stack three or four perfect fourths",
                            "Left hand plays root and fifth in low register",
                            "Right hand plays fourths in mid to high register"
                        ]
                    },
                    "exercises": [
                        {
                            "title": "Quartal Voicings on Dm7",
                            "description": "Build Tyner-style voicings over a D Dorian vamp.",
                            "exercise_type": "voicing",
                            "content": {
                                "chord": "Dm7",
                                "mode": "D Dorian",
                                "voicing_style": "Quartal"
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 20
                        }
                    ]
                }
            ]
        }
    ]
}

# ============================================================================
# SECTION 5: DEEPENED EXISTING CURRICULUM EXAMPLE
# ============================================================================
# This shows how to expand an existing curriculum with more lessons,
# exercises, and progressive difficulty

GOSPEL_KEYS_ESSENTIALS_EXPANDED = {
    "title": "Gospel Keys Essentials (Expanded Edition)",
    "description": "The definitive start to playing traditional and contemporary gospel. Master the 'church sound' through essential voicings, passing chords, and standard progressions. Now with advanced modules and comprehensive ear training.",
    "modules": [
        {
            "title": "Gospel Harmony Foundations",
            "description": "Moving from triads to the rich sound of 7th and 9th chords.",
            "theme": "gospel_basics",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["Major & Minor 7th Chords", "The 1-4-5 Gospel Style", "Basic Shout Patterns"],
            "lessons": [
                # Original lessons preserved
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
                        },
                        # NEW EXERCISE - Ear training component
                        {
                            "title": "Recognizing 7th Chord Qualities",
                            "description": "Train your ear to distinguish maj7, dom7, and min7 by sound.",
                            "exercise_type": "ear_training",
                            "content": {
                                "chord_types": ["Maj7", "Dom7", "Min7"],
                                "recognition_method": "quality"
                            },
                            "difficulty": "beginner",
                            "estimated_duration_minutes": 10
                        }
                    ]
                },
                {
                    "title": "The Preacher's Chord",
                    "description": "Mastering the dominant 7#9 chord used for shouts and accents.",
                    "week_number": 2,
                    "concepts": ["Dominant 7#9", "Tritones", "Blues Scale"],
                    "theory_content": {
                        "summary": "The #9 chord combines major and minor elements, creating the signature 'shout' sound of gospel.",
                        "key_points": [
                            "Contains both major 3rd and minor 10th (#9)",
                            "Creates harmonic tension perfect for climaxes",
                            "Often resolves down by half-step"
                        ]
                    },
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
                        },
                        # NEW EXERCISE - Transcription
                        {
                            "title": "Learn a Gospel Shout from Recording",
                            "description": "Transcribe a traditional gospel shout using the #9 chord.",
                            "exercise_type": "transcription",
                            "content": {
                                "song_suggestion": "Jesus is on the Mainline",
                                "artist_suggestion": "Traditional Gospel",
                                "focus": "Preacher's chord in context"
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 30
                        }
                    ]
                },
                # NEW LESSON - Fills the gap between week 2 and end of module
                {
                    "title": "9th and 11th Chords",
                    "description": "Extending harmony beyond 7ths for contemporary gospel sound.",
                    "week_number": 3,
                    "concepts": ["9th Chords", "11th Chords", "Upper Structure Voicings"],
                    "theory_content": {
                        "summary": "Contemporary gospel uses extended chords (9ths, 11ths, 13ths) for a lusher, more sophisticated sound.",
                        "key_points": [
                            "Add the 9th (one octave plus a second) to any 7th chord",
                            "11th chords work best on minor and dominant chords",
                            "Avoid the 11th on major chords unless it's #11"
                        ]
                    },
                    "exercises": [
                        {
                            "title": "Stacking Extensions",
                            "description": "Build Dm9, Dm11, G13 step by step.",
                            "exercise_type": "voicing",
                            "content": {
                                "progression": ["Dm7", "Dm9", "Dm11"],
                                "method": "Progressive stacking"
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 15
                        },
                        {
                            "title": "Contemporary Gospel Progression",
                            "description": "ii11-V13-Imaj9 with full extensions.",
                            "exercise_type": "progression",
                            "content": {
                                "chords": ["Dm11", "G13", "Cmaj9"],
                                "style": "Contemporary Gospel"
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 20
                        }
                    ]
                },
                # NEW LESSON - Practical application
                {
                    "title": "Hymn Reharmonization",
                    "description": "Taking simple hymns and adding gospel harmony.",
                    "week_number": 4,
                    "concepts": ["Reharmonization", "Substitution", "Passing Chords"],
                    "theory_content": {
                        "summary": "Gospel pianists reharmonize traditional hymns by adding 7ths, 9ths, and passing chords between the original harmonies.",
                        "key_points": [
                            "Start with the original hymn harmony",
                            "Add 7ths to all triads",
                            "Insert passing chords between main harmonies",
                            "Use secondary dominants to create movement"
                        ]
                    },
                    "exercises": [
                        {
                            "title": "Amazing Grace Gospel Style",
                            "description": "Reharmonize Amazing Grace with gospel chords.",
                            "exercise_type": "reharmonization",
                            "content": {
                                "song": "Amazing Grace",
                                "original_key": "G",
                                "techniques": ["Add 7ths", "Passing chords", "Secondary dominants"]
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 25
                        },
                        {
                            "title": "Ear Training: Recognizing Reharmonization",
                            "description": "Listen to gospel recordings and identify reharmonization techniques.",
                            "exercise_type": "ear_training",
                            "content": {
                                "skill": "Reharmonization recognition",
                                "songs": ["Traditional hymns in gospel style"]
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
                # Original lessons with expanded exercises
                {
                    "title": "The 7-3-6 Progression",
                    "description": "The classic gospel turnaround to the relative minor.",
                    "week_number": 5,
                    "concepts": ["Secondary Dominants", "Diminished Passing Chords"],
                    "theory_content": {
                        "summary": "The 7-3-6 progression uses secondary dominants to create strong harmonic movement to the vi chord (relative minor).",
                        "key_points": [
                            "vii°7 acts as passing chord",
                            "V7/vi (secondary dominant) creates tension",
                            "Resolves to vi minor chord with emotional impact"
                        ]
                    },
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
                        },
                        # NEW EXERCISES
                        {
                            "title": "7-3-6 in All Keys",
                            "description": "Practice the 7-3-6 pattern around the cycle.",
                            "exercise_type": "progression",
                            "content": {
                                "pattern": "7-3-6",
                                "practice": "all_keys"
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 30
                        },
                        {
                            "title": "Improvising Over 7-3-6",
                            "description": "Create right-hand melodies over the 7-3-6 progression.",
                            "exercise_type": "improvisation",
                            "content": {
                                "progression": "7-3-6",
                                "key": "Ab",
                                "approach": "Guide tones and gospel inflections"
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 25
                        }
                    ]
                },
                {
                    "title": "Walk-ups and Walk-downs",
                    "description": "Bass line movements that drive congregational songs.",
                    "week_number": 6,
                    "concepts": ["Bass Lines", "Slash Chords"],
                    "theory_content": {
                        "summary": "Walk-ups and walk-downs use chromatic or scalar bass movement to connect chords smoothly.",
                        "key_points": [
                            "Walk-up: ascending bass line between chords",
                            "Walk-down: descending bass line",
                            "Use slash chords to create smooth voice leading",
                            "Common in congregational singing"
                        ]
                    },
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
                        },
                        # NEW EXERCISES
                        {
                            "title": "Creating Your Own Walk-ups",
                            "description": "Compose walk-ups between I-IV-V chords.",
                            "exercise_type": "melody_harmonization",
                            "content": {
                                "task": "Create bass walks",
                                "chords": ["I", "IV", "V"],
                                "techniques": ["Chromatic", "Scalar", "Slash chords"]
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 20
                        },
                        {
                            "title": "Walking Bass in Gospel Context",
                            "description": "Learn authentic walking bass from gospel recordings.",
                            "exercise_type": "transcription",
                            "content": {
                                "focus": "Bass line movement",
                                "style": "Traditional gospel"
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 25
                        }
                    ]
                },
                # NEW LESSONS to fill out module
                {
                    "title": "The Gospel Turn-around",
                    "description": "Classic endings and turn-arounds used in gospel music.",
                    "week_number": 7,
                    "concepts": ["Turnarounds", "Endings", "Tag Progressions"],
                    "theory_content": {
                        "summary": "Gospel turnarounds are short progressions that lead back to the beginning of a song or create dramatic endings.",
                        "key_points": [
                            "I-VI-ii-V is the classic turnaround",
                            "Substitute secondary dominants for color",
                            "Tags repeat the turnaround for emphasis"
                        ]
                    },
                    "exercises": [
                        {
                            "title": "Classic Gospel Turnaround",
                            "description": "I-VI-ii-V with gospel voicings.",
                            "exercise_type": "progression",
                            "content": {
                                "chords": ["C", "A7", "Dm7", "G7"],
                                "style": "Gospel voicings"
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 15
                        },
                        {
                            "title": "Creating Tag Endings",
                            "description": "Repeat turnarounds with increasing intensity.",
                            "exercise_type": "improvisation",
                            "content": {
                                "concept": "Tag repetition",
                                "dynamics": "Building intensity"
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 20
                        }
                    ]
                },
                {
                    "title": "Gospel in Different Keys",
                    "description": "Transposing gospel progressions for different vocalists.",
                    "week_number": 8,
                    "concepts": ["Transposition", "Key Signatures", "Vocal Ranges"],
                    "theory_content": {
                        "summary": "Gospel pianists must be able to transpose songs quickly to accommodate different vocal ranges.",
                        "key_points": [
                            "Learn patterns, not just specific keys",
                            "Think in Roman numerals for easy transposition",
                            "Common gospel keys: Ab, Bb, Eb, F"
                        ]
                    },
                    "exercises": [
                        {
                            "title": "Transpose Gospel Progression",
                            "description": "Take a C major progression to Ab, Bb, and Eb.",
                            "exercise_type": "progression",
                            "content": {
                                "progression": "ii-V-I with walk-ups",
                                "target_keys": ["Ab", "Bb", "Eb"]
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 25
                        },
                        {
                            "title": "Sight-Reading Gospel Charts",
                            "description": "Practice reading chord charts and transposing on the fly.",
                            "exercise_type": "sight_reading",
                            "content": {
                                "chart_type": "Nashville numbers",
                                "skill": "Quick transposition"
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 20
                        }
                    ]
                }
            ]
        },
        # NEW MODULE - Advanced Gospel Techniques
        {
            "title": "Advanced Gospel Techniques",
            "description": "Master the advanced vocabulary of contemporary gospel including runs, fills, and modulations.",
            "theme": "gospel_advanced",
            "start_week": 9,
            "end_week": 12,
            "outcomes": ["Gospel Runs", "Dynamic Modulation", "Shout Sections"],
            "lessons": [
                {
                    "title": "Gospel Runs & Fills",
                    "description": "The flashy scalar and chromatic runs that punctuate gospel playing.",
                    "week_number": 9,
                    "concepts": ["Scalar Runs", "Chromatic Runs", "Rhythmic Placement"],
                    "theory_content": {
                        "summary": "Gospel runs are rapid scalar or chromatic passages used to fill space or create excitement between vocal phrases.",
                        "key_points": [
                            "Runs typically descend from high to low",
                            "Use pentatonic, blues, or chromatic scales",
                            "Place runs at natural phrase endings"
                        ]
                    },
                    "exercises": [
                        {
                            "title": "Basic Pentatonic Run",
                            "description": "Descending C pentatonic run ending on tonic.",
                            "exercise_type": "lick",
                            "content": {
                                "scale": "C Pentatonic",
                                "direction": "Descending",
                                "ending": "Tonic resolution"
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 15
                        },
                        {
                            "title": "Chromatic Gospel Run",
                            "description": "Fast chromatic run from octave down to tonic.",
                            "exercise_type": "lick",
                            "content": {
                                "type": "Chromatic",
                                "range": "One octave"
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 20
                        },
                        {
                            "title": "Transcribe Gospel Runs",
                            "description": "Learn authentic runs from gospel recordings.",
                            "exercise_type": "transcription",
                            "content": {
                                "focus": "Runs and fills",
                                "artists": ["Kirk Franklin", "Fred Hammond"]
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 30
                        }
                    ]
                },
                {
                    "title": "Gospel Modulations",
                    "description": "The dramatic key changes that elevate gospel songs.",
                    "week_number": 10,
                    "concepts": ["Modulation", "Key Changes", "Common Tone Modulation"],
                    "theory_content": {
                        "summary": "Gospel songs often modulate up by half-step or whole-step to increase intensity, especially near the end.",
                        "key_points": [
                            "Half-step up is most common",
                            "Use pivot chords or direct modulation",
                            "Prepare the congregation with a cue"
                        ]
                    },
                    "exercises": [
                        {
                            "title": "Half-Step Modulation",
                            "description": "Modulate from C to Db using a pivot chord.",
                            "exercise_type": "progression",
                            "content": {
                                "start_key": "C",
                                "end_key": "Db",
                                "method": "Pivot chord"
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 20
                        }
                    ]
                },
                {
                    "title": "The Gospel Shout Section",
                    "description": "High-energy endings with call-and-response and repetition.",
                    "week_number": 11,
                    "concepts": ["Call and Response", "Shout Chords", "Rhythmic Intensity"],
                    "exercises": [
                        {
                            "title": "Building a Shout",
                            "description": "Create a shout section with increasing intensity.",
                            "exercise_type": "improvisation",
                            "content": {
                                "structure": "Call and response",
                                "dynamics": "Building crescendo"
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 25
                        }
                    ]
                },
                {
                    "title": "Gospel Repertoire Capstone",
                    "description": "Learn a complete gospel song applying all techniques.",
                    "week_number": 12,
                    "concepts": ["Full Song", "Performance Practice"],
                    "exercises": [
                        {
                            "title": "Learn Complete Gospel Song",
                            "description": "Master a full contemporary gospel arrangement.",
                            "exercise_type": "repertoire",
                            "content": {
                                "song_suggestions": [
                                    "I Smile - Kirk Franklin",
                                    "Now Behold the Lamb - Kirk Franklin"
                                ],
                                "elements": ["Intro", "Verse", "Chorus", "Bridge", "Shout", "Ending"]
                            },
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 60
                        }
                    ]
                }
            ]
        }
    ]
}

# ============================================================================
# COMBINED CURRICULUM CATALOG
# ============================================================================

EXPANDED_CURRICULUMS = {
    # Original curriculums (reference - keep these in your system)
    "gospel_essentials": "See GOSPEL_KEYS_ESSENTIALS",
    "jazz_bootcamp": "See JAZZ_IMPROV_BOOTCAMP",
    "neosoul_mastery": "See NEO_SOUL_MASTERY",
    "contemporary_worship": "See CONTEMPORARY_WORSHIP",
    "blues_master": "See BLUES_MASTER_CLASS",
    "berklee_jazz": "See BERKLEE_JAZZ_ESSENTIALS",
    "classical_abrsm": "See CLASSICAL_ABRSM",
    "latin_rhythms": "See LATIN_RHYTHMS",
    "modern_rnb": "See MODERN_RNB_PRODUCER",
    "worship_band": "See WORSHIP_BAND_READY",
    
    # New genre curriculums
    "bebop_mastery": BEBOP_MASTERY,
    "stride_piano": STRIDE_PIANO,
    "funk_fundamentals": FUNK_PIANO,
    "country_honkytonk": COUNTRY_HONKYTONK,
    "modal_jazz": MODAL_JAZZ,
    
    # Expanded versions
    "gospel_essentials_expanded": GOSPEL_KEYS_ESSENTIALS_EXPANDED,
}

# ============================================================================
# SECTION 6: AI PROMPT TEMPLATES FOR DYNAMIC GENERATION
# ============================================================================
# These templates show how to use AI to generate personalized content

AI_PROMPT_TEMPLATES = {
    "exercise_generation": {
        "template": """
Generate a {difficulty} level {exercise_type} exercise for piano.

Genre: {genre}
Concept: {concept}
Key: {key}
Estimated Duration: {duration} minutes

The exercise should:
- Focus specifically on {concept}
- Be appropriate for {difficulty} level
- Include clear instructions
- Provide specific notes/chords when relevant
- Match the style characteristics of {genre}

Return the exercise in JSON format with fields:
- title
- description
- exercise_type
- content (specific to exercise type)
- difficulty
- estimated_duration_minutes
        """,
        "example_usage": {
            "difficulty": "intermediate",
            "exercise_type": "voicing",
            "genre": "gospel",
            "concept": "7th chords with gospel flavor",
            "key": "Eb",
            "duration": 15
        }
    },
    
    "progression_generation": {
        "template": """
Generate a chord progression for {genre} piano in the key of {key}.

Style characteristics needed:
- {style_features}

Difficulty: {difficulty}
Duration: {duration} measures

Include:
- Chord symbols
- Roman numeral analysis
- Voice leading suggestions
- Style-specific rhythmic feel

Return in JSON format.
        """,
        "example_usage": {
            "genre": "neo-soul",
            "key": "Dm",
            "style_features": "lush extensions, chromatic movement, laid-back feel",
            "difficulty": "advanced",
            "duration": 8
        }
    },
    
    "lick_variation": {
        "template": """
Take this {genre} lick and create {num_variations} variations:

Original lick: {original_lick_notes}
Key: {key}

Create variations using:
- Rhythmic displacement
- Different articulations
- Harmonic substitutions
- Extended techniques

Each variation should maintain the essential character while offering new flavors.
        """,
        "example_usage": {
            "genre": "bebop",
            "num_variations": 5,
            "original_lick_notes": "D-F-E-C-A-G-F-E",
            "key": "Dm7"
        }
    },
    
    "personalized_lesson": {
        "template": """
Create a personalized lesson plan for a student with these characteristics:

Current Level: {current_level}
Goals: {goals}
Weaknesses: {weaknesses}
Time Available: {time_per_week} hours/week
Preferred Genres: {genres}

Generate a {duration_weeks} week lesson plan that:
- Addresses their specific weaknesses
- Progresses toward their goals
- Incorporates their preferred genres
- Fits their time constraints
- Includes varied exercise types for engagement

Return structured lesson plan in JSON format.
        """,
        "example_usage": {
            "current_level": "intermediate",
            "goals": "Play in worship band, improve sight-reading",
            "weaknesses": "Weak left hand, limited chord vocabulary",
            "time_per_week": 5,
            "genres": ["contemporary_worship", "gospel"],
            "duration_weeks": 8
        }
    },
    
    "style_fusion": {
        "template": """
Create exercises that blend {genre1} and {genre2} concepts.

From {genre1}, emphasize: {genre1_concepts}
From {genre2}, emphasize: {genre2_concepts}

Generate {num_exercises} exercises that show how these styles intersect and complement each other.

This helps students see connections between genres and expand their musical vocabulary.
        """,
        "example_usage": {
            "genre1": "blues",
            "genre2": "jazz",
            "genre1_concepts": "12-bar form, blues scale, shuffle feel",
            "genre2_concepts": "ii-V-I, extended chords, walking bass",
            "num_exercises": 4
        }
    }
}

# ============================================================================
# SECTION 7: LEARNING PATH RECOMMENDATION ENGINE
# ============================================================================
# Logic for suggesting curriculum paths based on student profile

LEARNING_PATHS = {
    "complete_beginner": {
        "description": "For someone with no piano experience",
        "recommended_order": [
            ("classical_abrsm", "Build fundamental technique"),
            ("blues_master", "Develop feel and groove"),
            ("jazz_bootcamp", "Introduce chord voicings and improvisation"),
        ],
        "estimated_duration_months": 12
    },
    
    "church_musician": {
        "description": "For aspiring worship or gospel pianists",
        "recommended_order": [
            ("contemporary_worship", "Learn modern worship essentials"),
            ("gospel_essentials", "Add traditional gospel vocabulary"),
            ("worship_band", "Practical team skills"),
            ("gospel_essentials_expanded", "Advanced gospel techniques")
        ],
        "estimated_duration_months": 10
    },
    
    "jazz_focused": {
        "description": "For students wanting comprehensive jazz training",
        "recommended_order": [
            ("blues_master", "Foundation in blues and swing"),
            ("jazz_bootcamp", "Basic jazz concepts"),
            ("berklee_jazz", "Professional voicings"),
            ("bebop_mastery", "Advanced improvisation"),
            ("modal_jazz", "Modern approaches")
        ],
        "estimated_duration_months": 18
    },
    
    "producer_songwriter": {
        "description": "For beatmakers and R&B producers",
        "recommended_order": [
            ("modern_rnb", "Lo-fi and trap soul progressions"),
            ("neosoul_mastery", "Lush harmony and groove"),
            ("funk_fundamentals", "Rhythm and syncopation"),
            ("jazz_bootcamp", "Sophisticated chord progressions")
        ],
        "estimated_duration_months": 12
    },
    
    "versatile_pro": {
        "description": "Comprehensive training across all styles",
        "recommended_order": [
            ("classical_abrsm", "Technical foundation"),
            ("jazz_bootcamp", "Jazz basics"),
            ("blues_master", "Blues language"),
            ("gospel_essentials", "Gospel harmony"),
            ("latin_rhythms", "Latin grooves"),
            ("bebop_mastery", "Advanced jazz"),
            ("neosoul_mastery", "Contemporary R&B"),
            ("stride_piano", "Historic styles"),
            ("funk_fundamentals", "Funk vocabulary"),
            ("modal_jazz", "Modern concepts")
        ],
        "estimated_duration_months": 36
    }
}

# ============================================================================
# SECTION 8: PREREQUISITE AND DEPENDENCY MAPPING
# ============================================================================
# Shows which concepts must be learned before others

CONCEPT_PREREQUISITES = {
    "Bebop Scales": ["Major Scales", "Dominant 7th Chords", "Mixolydian Mode"],
    "Quartal Voicings": ["Intervals", "Chord Construction", "Major Scales"],
    "Gospel Runs": ["Pentatonic Scales", "Blues Scale", "Hand Coordination"],
    "Stride Left Hand": ["Octaves", "Basic Chords", "Hand Independence"],
    "Modal Improvisation": ["Seven Modes", "Scale Theory", "Basic Improvisation"],
    "Tritone Substitution": ["Dominant 7th", "ii-V-I Progression", "Voice Leading"],
    "Reharmonization": ["Chord Function", "ii-V-I", "Secondary Dominants"],
    "Clave Rhythms": ["Basic Rhythm Reading", "Syncopation", "Polyrhythm Basics"],
    "Shell Voicings": ["Chord Tones", "Inversions", "Voice Leading"],
    "Walking Bass": ["Scale Degrees", "Chord Tones", "Bass Line Movement"],
}

# ============================================================================
# SECTION 9: DIFFICULTY PROGRESSION FRAMEWORK
# ============================================================================
# Guidelines for scaling exercises by difficulty

DIFFICULTY_SCALING = {
    "beginner": {
        "tempo_range": "60-90 BPM",
        "key_complexity": "C, G, F major; A, D minor",
        "chord_types": "Triads, 7th chords",
        "rhythmic_complexity": "Quarter and eighth notes",
        "hand_coordination": "Mostly hands separate or simple together",
        "improvisation": "Guided, using pentatonic scales",
        "duration": "10-15 minutes per exercise"
    },
    
    "intermediate": {
        "tempo_range": "90-120 BPM",
        "key_complexity": "Up to 3 sharps/flats, relative minors",
        "chord_types": "7ths, 9ths, sus chords",
        "rhythmic_complexity": "16th notes, basic syncopation",
        "hand_coordination": "Hands together with independence",
        "improvisation": "Structured with chord tone emphasis",
        "duration": "15-25 minutes per exercise"
    },
    
    "advanced": {
        "tempo_range": "120-160 BPM",
        "key_complexity": "All keys, modes",
        "chord_types": "Extended chords (9, 11, 13), alterations",
        "rhythmic_complexity": "Complex syncopation, polyrhythms",
        "hand_coordination": "Full independence, contrapuntal",
        "improvisation": "Free with harmonic awareness",
        "duration": "20-35 minutes per exercise"
    },
    
    "expert": {
        "tempo_range": "160+ BPM",
        "key_complexity": "All keys, rapid modulation",
        "chord_types": "Upper structures, polychords, advanced reharmonization",
        "rhythmic_complexity": "Advanced polyrhythms, metric modulation",
        "hand_coordination": "Virtuosic independence",
        "improvisation": "Complete freedom, outside playing",
        "duration": "30-60 minutes per exercise"
    }
}

# ============================================================================
# SECTION 10: MIDI GENERATION PARAMETERS
# ============================================================================
# Configuration for generating MIDI files from exercises

MIDI_GENERATION_CONFIG = {
    "tempo_defaults": {
        "blues_master": 80,
        "gospel_essentials": 75,
        "jazz_bootcamp": 120,
        "bebop_mastery": 180,
        "neosoul_mastery": 85,
        "funk_fundamentals": 95,
        "worship_band": 70,
        "latin_rhythms": 110,
        "stride_piano": 140
    },
    
    "voicing_defaults": {
        "gospel": {
            "left_hand": "Shell voicing or bass note",
            "right_hand": "Full chord with extensions",
            "velocity": 80
        },
        "jazz": {
            "left_hand": "Rootless voicing",
            "right_hand": "Melody or comp",
            "velocity": 70
        },
        "classical": {
            "left_hand": "Bass + accompaniment",
            "right_hand": "Melody",
            "velocity": 75
        }
    },
    
    "exercise_generation": {
        "scale": {
            "include_fingering": True,
            "ascending_descending": True,
            "hands": ["separate", "together"]
        },
        "progression": {
            "include_rhythm": True,
            "voicing_style": "genre_appropriate",
            "duration_bars": 8
        },
        "lick": {
            "include_articulation": True,
            "show_phrasing": True,
            "loop": True
        }
    }
}

# ============================================================================
# SECTION 11: ASSESSMENT AND PROGRESS TRACKING
# ============================================================================
# Framework for evaluating student progress

SKILL_ASSESSMENT_FRAMEWORK = {
    "technical_skills": [
        {
            "skill": "Scale Fluency",
            "levels": {
                "beginner": "C, G, F major at 60 BPM, hands separate",
                "intermediate": "All major scales at 120 BPM, hands together",
                "advanced": "All major and minor scales at 160+ BPM with dynamics",
                "expert": "All scales, modes in thirds/sixths at high tempo"
            }
        },
        {
            "skill": "Chord Voicing",
            "levels": {
                "beginner": "Basic triads and 7th chords",
                "intermediate": "Shell voicings, rootless voicings",
                "advanced": "Extended chords, upper structures",
                "expert": "Complete reharmonization, polychords"
            }
        },
        {
            "skill": "Rhythm",
            "levels": {
                "beginner": "Quarter and eighth notes, basic timing",
                "intermediate": "16th notes, basic syncopation",
                "advanced": "Complex syncopation, polyrhythm",
                "expert": "Advanced polyrhythm, metric modulation"
            }
        },
        {
            "skill": "Improvisation",
            "levels": {
                "beginner": "Pentatonic over one chord",
                "intermediate": "Chord tones over ii-V-I",
                "advanced": "Bebop scales, approach notes, outside playing",
                "expert": "Complete freedom, advanced harmonic concepts"
            }
        },
        {
            "skill": "Sight Reading",
            "levels": {
                "beginner": "Simple melodies, both clefs",
                "intermediate": "Lead sheets with chord symbols",
                "advanced": "Complex notation, quick transposition",
                "expert": "Dense scores, instant transposition"
            }
        }
    ],
    
    "style_competencies": {
        "gospel": ["7th chords", "Walk-ups", "Shouts", "Reharmonization"],
        "jazz": ["ii-V-I", "Shell voicings", "Walking bass", "Bebop lines"],
        "blues": ["12-bar form", "Blues scale", "Shuffle", "Turnarounds"],
        "neosoul": ["Minor 11", "Tritone subs", "Grace notes", "Dilla feel"],
        "classical": ["Proper technique", "Dynamics", "Phrasing", "Repertoire"]
    }
}

# ============================================================================
# SECTION 12: PRACTICE ROUTINE GENERATOR
# ============================================================================
# Creates balanced daily practice schedules

PRACTICE_ROUTINE_TEMPLATE = {
    "warmup": {
        "duration_minutes": 10,
        "activities": [
            "Scales in target key",
            "Hanon exercises or similar",
            "Chord progressions slowly"
        ]
    },
    
    "technical_work": {
        "duration_minutes": 15,
        "activities": [
            "Current exercise from curriculum",
            "Focus on weak areas",
            "Gradual tempo increase"
        ]
    },
    
    "concept_learning": {
        "duration_minutes": 20,
        "activities": [
            "New voicings or progressions",
            "Theory application",
            "Listening and transcribing"
        ]
    },
    
    "creative_practice": {
        "duration_minutes": 15,
        "activities": [
            "Improvisation",
            "Composition",
            "Playing along with recordings"
        ]
    },
    
    "repertoire": {
        "duration_minutes": 20,
        "activities": [
            "Working on full songs",
            "Performance practice",
            "Recording yourself"
        ]
    },
    
    "cooldown": {
        "duration_minutes": 10,
        "activities": [
            "Play something you love",
            "Review what you learned",
            "Set goals for next session"
        ]
    }
}

# ============================================================================
# USAGE EXAMPLE: HOW TO USE THIS SYSTEM
# ============================================================================

USAGE_EXAMPLES = """
# Example 1: Generate a personalized exercise for a student
def generate_exercise_for_student(student_profile):
    # Use AI with the template
    prompt = AI_PROMPT_TEMPLATES["exercise_generation"]["template"].format(
        difficulty=student_profile["level"],
        exercise_type="voicing",
        genre=student_profile["preferred_genre"],
        concept="Shell voicings",
        key="Bb",
        duration=15
    )
    # Send to AI, get structured exercise back
    return ai_generate(prompt)

# Example 2: Create a learning path for a church musician
def create_church_musician_path():
    path = LEARNING_PATHS["church_musician"]
    curriculums = []
    for curriculum_id, reason in path["recommended_order"]:
        curriculum = EXPANDED_CURRICULUMS[curriculum_id]
        curriculums.append({
            "curriculum": curriculum,
            "reason": reason
        })
    return curriculums

# Example 3: Check if a student is ready for a concept
def check_prerequisites(student_skills, target_concept):
    required = CONCEPT_PREREQUISITES.get(target_concept, [])
    return all(skill in student_skills for skill in required)

# Example 4: Generate MIDI for an exercise
def generate_midi_for_exercise(exercise, genre):
    tempo = MIDI_GENERATION_CONFIG["tempo_defaults"][genre]
    voicing = MIDI_GENERATION_CONFIG["voicing_defaults"][genre]
    # Use these parameters to generate MIDI file
    return create_midi(exercise, tempo, voicing)

# Example 5: Bridge between genres
def get_bridge_concepts(from_genre, to_genre):
    bridge_key = f"{from_genre}_to_{to_genre}"
    if bridge_key in CURRICULUM_BRIDGES:
        return CURRICULUM_BRIDGES[bridge_key]
    return None

# Example 6: Create a practice routine
def create_daily_practice(duration_minutes, student_level, focus_areas):
    routine = PRACTICE_ROUTINE_TEMPLATE.copy()
    # Adjust durations based on available time
    # Select exercises matching student level
    # Emphasize focus areas
    return customized_routine

# Example 7: Assess student progress
def assess_student(student, skill_category):
    framework = SKILL_ASSESSMENT_FRAMEWORK[skill_category]
    # Test student on each skill
    # Compare to level descriptions
    return assessment_results
"""

# ============================================================================
# FINAL NOTES
# ============================================================================

IMPLEMENTATION_NOTES = """
KEY PRINCIPLES FOR EXPANSION:

1. MODULARITY
   - Each curriculum, module, lesson, and exercise is self-contained
   - Can be mixed and matched based on student needs
   - AI can generate variants while preserving structure

2. PROGRESSIVE DIFFICULTY
   - Always start with fundamentals
   - Build complexity gradually
   - Provide multiple entry points for different skill levels

3. CROSS-POLLINATION
   - Show connections between genres
   - Help students transfer knowledge
   - Encourage stylistic fusion

4. AI INTEGRATION
   - Use AI for personalization, not replacement
   - Templates ensure consistent quality
   - Human expertise guides the system

5. PRACTICAL FOCUS
   - Every exercise should be playable and musical
   - Include real-world applications
   - Build toward actual performance

6. ASSESSMENT-DRIVEN
   - Regular skill checks guide progression
   - Identify weaknesses systematically
   - Celebrate achievements

7. MULTIMEDIA APPROACH
   - Generate MIDI for audio learning
   - Include video references
   - Provide written theory alongside practice

8. COMMUNITY BUILDING
   - Enable sharing of custom exercises
   - Allow teachers to create curriculums
   - Foster peer learning

NEXT STEPS FOR YOUR APP:

1. Implement the data structures shown here
2. Create AI generation functions using the templates
3. Build a recommendation engine for learning paths
4. Develop MIDI generation for all exercise types
5. Add progress tracking and assessment
6. Create a practice routine generator
7. Build cross-curriculum bridge lessons
8. Add social/sharing features

This system is designed to scale indefinitely while maintaining
pedagogical coherence. You can add new genres, exercises, and
concepts without breaking existing functionality.
"""

print("Expanded Piano Curriculum System loaded successfully!")
print(f"Total curriculums available: {len(EXPANDED_CURRICULUMS)}")
print(f"Cross-curriculum bridges: {len(CURRICULUM_BRIDGES)}")
print(f"Learning paths: {len(LEARNING_PATHS)}")
print(f"Exercise types: {len(EXERCISE_TYPES)}")