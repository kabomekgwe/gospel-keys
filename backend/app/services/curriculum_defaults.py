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

BLUES_MASTER_CLASS = {
    "title": "Blues Master Class",
    "description": "Master authentic blues piano from the ground up. Learn 12-bar blues, turnarounds, shuffle rhythms, and classic licks from the masters.",
    "modules": [
        {
            "title": "Blues Fundamentals",
            "description": "The backbone of blues piano: 12-bar form and the blues scale.",
            "theme": "blues_basics",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["12-Bar Blues Form", "Blues Scale Mastery", "Dominant 7th Voicings"],
            "lessons": [
                {
                    "title": "The 12-Bar Blues Form",
                    "description": "Understanding the I-IV-V structure that defines the blues.",
                    "week_number": 1,
                    "concepts": ["12-Bar Form", "Dominant 7ths", "Shuffle Feel"],
                    "exercises": [
                        {
                            "title": "Basic 12-Bar in C",
                            "description": "Play the classic C7-F7-G7 progression with proper form.",
                            "exercise_type": "progression",
                            "content": {
                                "chords": ["C7", "C7", "C7", "C7", "F7", "F7", "C7", "C7", "G7", "F7", "C7", "G7"],
                                "key": "C"
                            },
                            "difficulty": "beginner",
                            "estimated_duration_minutes": 20
                        }
                    ]
                },
                {
                    "title": "The Blues Scale",
                    "description": "Adding the 'blue notes' that give the blues its soulful sound.",
                    "week_number": 2,
                    "concepts": ["Minor Pentatonic", "Blue Note (b5)", "Call and Response"],
                    "exercises": [
                        {
                            "title": "C Blues Scale Patterns",
                            "description": "Practice the C blues scale in all octaves.",
                            "exercise_type": "scale",
                            "content": {
                                "scale": "C Blues",
                                "notes": ["C", "Eb", "F", "Gb", "G", "Bb", "C"]
                            },
                            "difficulty": "beginner",
                            "estimated_duration_minutes": 15
                        }
                    ]
                }
            ]
        },
        {
            "title": "Blues Turnarounds & Licks",
            "description": "Classic turnarounds and signature licks from blues legends.",
            "theme": "blues_advanced",
            "start_week": 5,
            "end_week": 8,
            "outcomes": ["Classic Turnarounds", "Intro Licks", "Ending Tags"],
            "lessons": [
                {
                    "title": "The Classic Turnaround",
                    "description": "The I-VI-ii-V turnaround that sets up the next chorus.",
                    "week_number": 5,
                    "concepts": ["Turnarounds", "Chromatic Movement", "Walking Bass"],
                    "exercises": [
                        {
                            "title": "Standard Blues Turnaround in C",
                            "description": "C7 - A7 - Dm7 - G7 with walking bass.",
                            "exercise_type": "progression",
                            "content": {
                                "chords": ["C7", "A7", "Dm7", "G7"],
                                "key": "C"
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 20
                        }
                    ]
                }
            ]
        }
    ]
}

BERKLEE_JAZZ_ESSENTIALS = {
    "title": "Berklee Jazz Essentials",
    "description": "A Berklee-inspired jazz curriculum covering shell voicings, guide tones, ii-V-I mastery, and beginning improvisation techniques.",
    "modules": [
        {
            "title": "Jazz Voicings Foundation",
            "description": "Left-hand voicings that free your right hand for melodies.",
            "theme": "jazz_voicings",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["Shell Voicings (A & B Forms)", "Rootless Voicings", "Voice Leading"],
            "lessons": [
                {
                    "title": "Shell Voicings: Root-3rd-7th",
                    "description": "The essential left-hand voicings used by jazz professionals.",
                    "week_number": 1,
                    "concepts": ["Shell Voicings", "A Form (R-3-7)", "B Form (R-7-3)"],
                    "exercises": [
                        {
                            "title": "ii-V-I Shells Through All Keys",
                            "description": "Play Dm7-G7-Cmaj7 shells around the cycle of 4ths.",
                            "exercise_type": "voicing",
                            "content": {
                                "pattern": "ii-V-I Cycle",
                                "voicing_type": "shell"
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 25
                        }
                    ]
                },
                {
                    "title": "Rootless Voicings",
                    "description": "Drop the root for smoother, more sophisticated harmony.",
                    "week_number": 2,
                    "concepts": ["Type A Rootless", "Type B Rootless", "Tensions"],
                    "exercises": [
                        {
                            "title": "Rootless ii-V-I",
                            "description": "Practice rootless voicings with the bassist playing roots.",
                            "exercise_type": "voicing",
                            "difficulty": "advanced",
                            "estimated_duration_minutes": 20
                        }
                    ]
                }
            ]
        },
        {
            "title": "Jazz Standards & Improvisation",
            "description": "Apply your voicings to real jazz standards and begin soloing.",
            "theme": "jazz_standards",
            "start_week": 5,
            "end_week": 10,
            "outcomes": ["Standard Repertoire", "Chord Tone Soloing", "Approach Notes"],
            "lessons": [
                {
                    "title": "Your First Jazz Standard: Autumn Leaves",
                    "description": "Learn the harmony and melody of this essential standard.",
                    "week_number": 5,
                    "concepts": ["ii-V-I Major", "ii-V-i Minor", "Form (AABA)"],
                    "exercises": [
                        {
                            "title": "Autumn Leaves Head",
                            "description": "Play the melody with left-hand shell voicings.",
                            "exercise_type": "repertoire",
                            "content": {
                                "song": "Autumn Leaves",
                                "key": "Gm"
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 30
                        }
                    ]
                }
            ]
        }
    ]
}

CLASSICAL_ABRSM = {
    "title": "Classical Piano: ABRSM Grades 1-3",
    "description": "A structured classical piano curriculum inspired by ABRSM grading. Covers scales, arpeggios, sight-reading, and graded repertoire.",
    "modules": [
        {
            "title": "Grade 1: Foundations",
            "description": "Building proper technique and musicality from the start.",
            "theme": "classical_grade1",
            "start_week": 1,
            "end_week": 5,
            "outcomes": ["C & G Major Scales", "Basic Arpeggios", "Simple Repertoire"],
            "lessons": [
                {
                    "title": "Scales: C & G Major",
                    "description": "Two-octave scales with proper fingering.",
                    "week_number": 1,
                    "concepts": ["Scale Fingering", "Hand Position", "Thumb Under"],
                    "exercises": [
                        {
                            "title": "C Major Scale (2 Octaves)",
                            "description": "Hands separate, then together at 60 BPM.",
                            "exercise_type": "scale",
                            "content": {
                                "scale": "C Major",
                                "octaves": 2
                            },
                            "difficulty": "beginner",
                            "estimated_duration_minutes": 10
                        }
                    ]
                },
                {
                    "title": "Arpeggios: C & G Major",
                    "description": "Two-octave arpeggios with smooth thumb crossings.",
                    "week_number": 2,
                    "concepts": ["Arpeggio Fingering", "Wrist Rotation"],
                    "exercises": [
                        {
                            "title": "C Major Arpeggio (2 Octaves)",
                            "description": "C-E-G pattern, hands separate.",
                            "exercise_type": "arpeggio",
                            "difficulty": "beginner",
                            "estimated_duration_minutes": 10
                        }
                    ]
                }
            ]
        },
        {
            "title": "Grade 2: Expanding Technique",
            "description": "More keys, faster tempos, and expressive playing.",
            "theme": "classical_grade2",
            "start_week": 6,
            "end_week": 10,
            "outcomes": ["D, F, Bb Major Scales", "Am, Dm Scales", "Dynamics & Phrasing"],
            "lessons": [
                {
                    "title": "Minor Scales: A & D Natural Minor",
                    "description": "Introduction to minor mode and its emotional quality.",
                    "week_number": 6,
                    "concepts": ["Natural Minor", "Relative Major/Minor"],
                    "exercises": [
                        {
                            "title": "A Natural Minor Scale",
                            "description": "Two octaves, hands together at 72 BPM.",
                            "exercise_type": "scale",
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 10
                        }
                    ]
                }
            ]
        }
    ]
}

LATIN_RHYTHMS = {
    "title": "Latin Piano Rhythms",
    "description": "Unlock the rhythmic world of Latin piano. Learn bossa nova, salsa montuno, Afro-Cuban patterns, and clave-based grooves.",
    "modules": [
        {
            "title": "Bossa Nova Essentials",
            "description": "The smooth Brazilian groove that changed jazz.",
            "theme": "latin_bossa",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["Bossa Nova Rhythm", "Chord Voicings", "Bass Patterns"],
            "lessons": [
                {
                    "title": "The Bossa Nova Groove",
                    "description": "The iconic left-hand pattern behind Girl from Ipanema.",
                    "week_number": 1,
                    "concepts": ["Syncopation", "Bass + Chord Pattern", "Anticipations"],
                    "exercises": [
                        {
                            "title": "Classic Bossa Pattern in Dm",
                            "description": "Root on beat 1, chord anticipating beat 2.",
                            "exercise_type": "rhythm",
                            "content": {
                                "key": "Dm",
                                "pattern": "Bossa Nova"
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 20
                        }
                    ]
                }
            ]
        },
        {
            "title": "Salsa Montuno",
            "description": "The driving piano pattern behind salsa music.",
            "theme": "latin_salsa",
            "start_week": 5,
            "end_week": 8,
            "outcomes": ["2-3 Clave", "Montuno Patterns", "Salsa Harmony"],
            "lessons": [
                {
                    "title": "Understanding Clave",
                    "description": "The rhythmic key that unlocks all Afro-Cuban music.",
                    "week_number": 5,
                    "concepts": ["2-3 Clave", "3-2 Clave", "Clave Direction"],
                    "exercises": [
                        {
                            "title": "Clapping Clave Patterns",
                            "description": "Internalize the clave before playing.",
                            "exercise_type": "rhythm",
                            "difficulty": "beginner",
                            "estimated_duration_minutes": 10
                        }
                    ]
                }
            ]
        }
    ]
}

MODERN_RNB_PRODUCER = {
    "title": "Modern R&B Producer Keys",
    "description": "Keyboard techniques for R&B and hip-hop production. Lo-fi chords, trap soul progressions, and the sounds behind modern hits.",
    "modules": [
        {
            "title": "Lo-Fi & Chill Chords",
            "description": "The dreamy, nostalgic sounds of lo-fi hip-hop.",
            "theme": "rnb_lofi",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["Major 7th Voicings", "9th & 11th Extensions", "Detuned Piano Sound"],
            "lessons": [
                {
                    "title": "Lo-Fi Chord Stacks",
                    "description": "Creating lush, jazzy chords for beats.",
                    "week_number": 1,
                    "concepts": ["Maj7/9 Voicings", "Add9 Chords", "Cluster Voicings"],
                    "exercises": [
                        {
                            "title": "Lo-Fi ii-V-I",
                            "description": "Dm9 - G13 - Cmaj9 with lo-fi voicings.",
                            "exercise_type": "progression",
                            "content": {
                                "chords": ["Dm9", "G13", "Cmaj9"],
                                "style": "lo-fi"
                            },
                            "difficulty": "intermediate",
                            "estimated_duration_minutes": 15
                        }
                    ]
                }
            ]
        },
        {
            "title": "Trap Soul Progressions",
            "description": "Dark, emotional progressions used in modern R&B.",
            "theme": "rnb_trapsoul",
            "start_week": 5,
            "end_week": 8,
            "outcomes": ["Minor Key Progressions", "808 Bass Awareness", "Melancholic Voicings"],
            "lessons": [
                {
                    "title": "The Trap Soul Sound",
                    "description": "Bryson Tiller, 6LACK, and the melancholic minor vibe.",
                    "week_number": 5,
                    "concepts": ["i-VI-III-VII", "Minor 9ths", "Sparse Voicings"],
                    "exercises": [
                        {
                            "title": "Classic Trap Soul Progression",
                            "description": "Am9 - Fmaj7 - Cmaj7 - G with 808 bass in mind.",
                            "exercise_type": "progression",
                            "content": {
                                "chords": ["Am9", "Fmaj7", "Cmaj7", "G"],
                                "key": "Am"
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

WORSHIP_BAND_READY = {
    "title": "Worship Band Ready",
    "description": "Practical keyboard skills for playing in a worship band. Nashville numbers, team dynamics, pad textures, and leading with confidence.",
    "modules": [
        {
            "title": "Worship Keys Fundamentals",
            "description": "Essential skills for fitting into a worship band.",
            "theme": "worship_fundamentals",
            "start_week": 1,
            "end_week": 4,
            "outcomes": ["Nashville Number System", "Pad Playing", "Team Dynamics"],
            "lessons": [
                {
                    "title": "The Nashville Number System",
                    "description": "Transpose any song instantly using numbers.",
                    "week_number": 1,
                    "concepts": ["Number System", "Transposition", "Chord Charts"],
                    "exercises": [
                        {
                            "title": "1-5-6-4 in Every Key",
                            "description": "The most common worship progression, all 12 keys.",
                            "exercise_type": "progression",
                            "content": {
                                "roman_numerals": ["I", "V", "vi", "IV"],
                                "practice": "all_keys"
                            },
                            "difficulty": "beginner",
                            "estimated_duration_minutes": 20
                        }
                    ]
                },
                {
                    "title": "Playing Pads & Textures",
                    "description": "Creating atmosphere without stepping on other instruments.",
                    "week_number": 2,
                    "concepts": ["Pad Sounds", "Sustained Chords", "Less is More"],
                    "exercises": [
                        {
                            "title": "Whole Note Pad Exercise",
                            "description": "Hold each chord for 4 bars, focusing on smooth transitions.",
                            "exercise_type": "rhythm",
                            "difficulty": "beginner",
                            "estimated_duration_minutes": 10
                        }
                    ]
                }
            ]
        },
        {
            "title": "Leading & Dynamics",
            "description": "Taking ownership of the keys role in worship.",
            "theme": "worship_leading",
            "start_week": 5,
            "end_week": 8,
            "outcomes": ["Building Dynamics", "Intro/Outro Creation", "Spontaneous Worship"],
            "lessons": [
                {
                    "title": "Building Dynamics",
                    "description": "Taking the congregation from quiet reflection to full praise.",
                    "week_number": 5,
                    "concepts": ["Crescendo", "Register Changes", "Rhythmic Intensity"],
                    "exercises": [
                        {
                            "title": "Dynamic Build Exercise",
                            "description": "Start with pads, add rhythm, build to full chords.",
                            "exercise_type": "dynamics",
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
    "blues_master": BLUES_MASTER_CLASS,
    "berklee_jazz": BERKLEE_JAZZ_ESSENTIALS,
    "classical_abrsm": CLASSICAL_ABRSM,
    "latin_rhythms": LATIN_RHYTHMS,
    "modern_rnb": MODERN_RNB_PRODUCER,
    "worship_band": WORSHIP_BAND_READY,
}
