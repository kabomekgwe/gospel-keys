"""
# DATASET: NEO_SOUL_MASTERY_DB
WEEKS: 1 - 16
FORMAT: GENERATIVE ENGINE READY
"""

# NEO_SOUL_DB
NEO_SOUL_DB = {
    "meta": {
        "genre": "Neo-Soul",
        "bpm_default": 85,
        "swing_default": 0.55,  # Slight swing by default
        "description": "The intersection of Jazz, Hip-Hop, and R&B."
    },
    "weeks": [
        # ==============================================================================
        # PHASE 1: HARMONIC FOUNDATIONS (WEEKS 1-4)
        # Focus: Building the lush, extended chord vocabulary.
        # ==============================================================================
        {
            "week": 1,
            "title": "The Minor 11th Aesthetic",
            "focus": "Voicing Construction",
            "theory_prompt": "Neo-Soul replaces minor triads with Minor 11ths. The clash between the b3 and 11 creates the vibe.",
            "exercises": [
                {
                    "id": "ns_wk1_ex1",
                    "name": "The 'So What' Stack",
                    "type": "voicing_static",
                    "instructions": "Play quartal voicings in the right hand over a root in the left.",
                    "engine_data": {
                        "keys": ["D", "Eb", "E"],
                        "voicing_stack": [0, 10, 15, 20, 24], # Root, b7, b3, 11, 1 (Stacked 4ths)
                        "velocity_range": (45, 65),
                        "timing_humanize": 0.05, # Slight roll
                        "sustain": True
                    }
                },
                {
                    "id": "ns_wk1_ex2",
                    "name": "The Cluster Grip (m9)",
                    "type": "voicing_static",
                    "instructions": "Keep the 9 and b3 adjacent in the voicing.",
                    "engine_data": {
                        "keys": ["C", "F", "G"],
                        "voicing_stack": [0, 7, 10, 14, 15], # Root, 5, b7, 9, b3 (The 9/b3 rub)
                        "velocity_range": (50, 70),
                        "timing_humanize": 0.0
                    }
                }
            ]
        },
        {
            "week": 2,
            "title": "Major 9th & Lydian Colors",
            "focus": "Major Chord Extensions",
            "theory_prompt": "Major chords in Neo-Soul are never just triads. We add the 9th and often the #11 (Lydian).",
            "exercises": [
                {
                    "id": "ns_wk2_ex1",
                    "name": "Major 9 Shells",
                    "type": "progression",
                    "instructions": "Move Major 9 chords through the Cycle of 4ths.",
                    "engine_data": {
                        "progression_intervals": [5, 5, 5, 5], # Movement by 4ths
                        "voicing_stack": [0, 4, 7, 11, 14], # R, 3, 5, 7, 9
                        "velocity_range": (60, 80),
                        "rhythm_grid": "1.......", # Whole notes
                    }
                },
                {
                    "id": "ns_wk2_ex2",
                    "name": "The Lydian Grip",
                    "type": "voicing_static",
                    "instructions": "Add the #11 to the top of the voicing.",
                    "engine_data": {
                        "keys": ["Eb", "Db"],
                        "voicing_stack": [0, 4, 7, 11, 14, 18], # R, 3, 5, 7, 9, #11
                        "velocity_range": (40, 60) # Play soft
                    }
                }
            ]
        },
        {
            "week": 3,
            "title": "Dominant Alterations",
            "focus": "Tension Chords",
            "theory_prompt": "The V chord needs tension. We use the Altered Scale (Alt) or 7#9.",
            "exercises": [
                {
                    "id": "ns_wk3_ex1",
                    "name": "The Voodoo Chord (7#9)",
                    "type": "rhythm_stab",
                    "instructions": "Short, sharp hits on the dominant.",
                    "engine_data": {
                        "keys": ["E", "A", "D"],
                        "voicing_stack": [0, 4, 10, 15], # R, 3, b7, #9
                        "velocity_range": (90, 110), # Hard hits
                        "duration_beat": 0.25 # Staccato
                    }
                }
            ]
        },
        {
            "week": 4,
            "title": "Tritone Substitution",
            "focus": "Harmonic Movement",
            "theory_prompt": "Swap the V chord for the bII7 to create chromatic bass movement.",
            "exercises": [
                {
                    "id": "ns_wk4_ex1",
                    "name": "2-5-1 Reharm",
                    "type": "progression",
                    "instructions": "Play ii-V-I, then ii-bII-I.",
                    "engine_data": {
                        "key": "C",
                        "chords": [
                            {"root": 2, "quality": "m9", "stack": [0, 3, 7, 10, 14]},   # Dm9
                            {"root": 1, "quality": "dom13#11", "stack": [0, 4, 10, 14, 18, 21]}, # Db13#11 (SubV)
                            {"root": 0, "quality": "maj9", "stack": [0, 4, 7, 11, 14]}  # Cmaj9
                        ],
                        "velocity_curve": "swell"
                    }
                }
            ]
        },
        # ==============================================================================
        # PHASE 2: RHYTHM & FEEL (WEEKS 5-8)
        # Focus: The "Dilla" feel, displacement, and bass interaction.
        # ==============================================================================
        {
            "week": 5,
            "title": "The 'Dilla' Time Feel",
            "focus": "Micro-timing",
            "theory_prompt": "The 'Drunk' feel comes from delaying the snare or the chords while the kick stays straight.",
            "exercises": [
                {
                    "id": "ns_wk5_ex1",
                    "name": "The Dragged Backbeat",
                    "type": "rhythm_grid",
                    "instructions": "Play chords strictly on beat 2 and 4, but 30ms late.",
                    "engine_data": {
                        "chord": "Am11",
                        "rhythm_pattern": [0, 1, 0, 1], # Beats 2 and 4
                        "grid_offset_ms": 35, # The Dilla Lag
                        "swing_percentage": 0.0 # Straight but offset
                    }
                },
                {
                    "id": "ns_wk5_ex2",
                    "name": "Quintuplet Swing",
                    "type": "scale_rhythm",
                    "instructions": "Play scales with a 'loping' 5:1 swing feel.",
                    "engine_data": {
                        "scale": "C Major",
                        "swing_percentage": 0.60, # Heavy swing
                        "velocity_accent": "offbeats"
                    }
                }
            ]
        },
        {
            "week": 6,
            "title": "Neo-Soul Bass Lines",
            "focus": "Left Hand Groove",
            "theory_prompt": "Synth bass lines often use slides and held roots with staccato octaves.",
            "exercises": [
                {
                    "id": "ns_wk6_ex1",
                    "name": "Root-Octave Slap",
                    "type": "bass_line",
                    "instructions": "Hold the low root, slap the upper octave on syncopated 16ths.",
                    "engine_data": {
                        "key": "Eb",
                        "pattern_grid": "1..a2..&3..e4...", # Rhythmic notation
                        "velocity_layers": {
                            "low_note": 100,
                            "high_note": 85
                        }
                    }
                }
            ]
        },
        {
            "week": 7,
            "title": "Grace Notes & Slides",
            "focus": "Melodic Ornamentation",
            "theory_prompt": "Mimic the guitar 'hammer-on' by sliding from b3 to 3.",
            "exercises": [
                {
                    "id": "ns_wk7_ex1",
                    "name": "The Pentatonic Slide",
                    "type": "lick_generator",
                    "instructions": "Slide b3->3 over every Major chord.",
                    "engine_data": {
                        "base_triad": [0, 4, 7],
                        "grace_note": 3, # The b3 interval
                        "target_note": 4, # The 3 interval
                        "slide_speed_ms": 40
                    }
                }
            ]
        },
        {
            "week": 8,
            "title": "The 'Lay Back' Groove",
            "focus": "Ensemble Timing",
            "theory_prompt": "Playing extremely behind the beat without losing the tempo.",
            "exercises": [
                {
                    "id": "ns_wk8_ex1",
                    "name": "Metronome Resistance",
                    "type": "rhythm_challenge",
                    "instructions": "Play chords consistently 50ms behind the click.",
                    "engine_data": {
                        "bpm": 80,
                        "click_track": True,
                        "target_latency_ms": 50,
                        "tolerance_ms": 10
                    }
                }
            ]
        },
        # ==============================================================================
        # PHASE 3: ADVANCED HARMONY (WEEKS 9-12)
        # Focus: Passing chords, secondary dominants, and reharmonization.
        # ==============================================================================
        {
            "week": 9,
            "title": "Secondary Dominants",
            "focus": "Functional Harmony",
            "theory_prompt": "Use V of V to target the next chord.",
            "exercises": [
                {
                    "id": "ns_wk9_ex1",
                    "name": "Chain of Dominants",
                    "type": "progression",
                    "instructions": "E7 -> A7 -> Dm9 -> G13 -> Cmaj9",
                    "engine_data": {
                        "key": "C",
                        "chords": [
                            {"root": 4, "quality": "dom7alt", "stack": [0, 4, 10, 13, 20]}, # E7b13
                            {"root": 9, "quality": "dom9", "stack": [0, 4, 10, 14]},        # A9
                            {"root": 2, "quality": "min9", "stack": [0, 3, 7, 10, 14]}      # Dm9
                        ]
                    }
                }
            ]
        },
        {
            "week": 10,
            "title": "Passing Diminished Chords",
            "focus": "Chromatic Connectors",
            "theory_prompt": "Connect chords a whole step apart with a diminished chord in between.",
            "exercises": [
                {
                    "id": "ns_wk10_ex1",
                    "name": "The Gospel Pass",
                    "type": "progression",
                    "instructions": "Cmaj7 -> C#dim7 -> Dm9",
                    "engine_data": {
                        "progression": ["I", "#i_dim7", "ii"],
                        "voicing_stack_dim": [0, 3, 6, 9] # Fully diminished
                    }
                }
            ]
        },
        {
            "week": 11,
            "title": "Constant Structure",
            "focus": "Parallel Motion",
            "theory_prompt": "Take a complex voicing and move it chromatically or in minor 3rds.",
            "exercises": [
                {
                    "id": "ns_wk11_ex1",
                    "name": "Parallel Minor 9s",
                    "type": "pattern",
                    "instructions": "Play Cm9 -> Bbm9 -> Abm9 (Planing).",
                    "engine_data": {
                        "shape_lock": True, # Keep exact interval structure
                        "intervals": [0, 3, 7, 10, 14],
                        "root_movement": [-2, -2] # Whole steps down
                    }
                }
            ]
        },
        {
            "week": 12,
            "title": "Reharmonization: The Basics",
            "focus": "Song Alteration",
            "theory_prompt": "Re-write a simple melody with Neo-Soul chords.",
            "exercises": [
                {
                    "id": "ns_wk12_ex1",
                    "name": "Mary Had a Little Lamb (Neo-Mix)",
                    "type": "reharm",
                    "instructions": "Harmonize the melody note 'E' with Cmaj9, then A13, then F#m11.",
                    "engine_data": {
                        "melody_note": 4, # E
                        "chord_options": ["Imaj9", "VI13", "#iv_m11"]
                    }
                }
            ]
        },
        # ==============================================================================
        # PHASE 4: PROFESSIONAL POLISH (WEEKS 13-16)
        # Focus: Licks, runs, improvisation, and specific artist styles.
        # ==============================================================================
        {
            "week": 13,
            "title": "Pentatonic Runs",
            "focus": "Soloing Vocabulary",
            "theory_prompt": "Fast, sweeping runs using the pentatonic scale.",
            "exercises": [
                {
                    "id": "ns_wk13_ex1",
                    "name": "The 'Sweep'",
                    "type": "lick_generator",
                    "instructions": "Ascending pentatonic run, 32nd notes.",
                    "engine_data": {
                        "scale": "pentatonic_major",
                        "speed": "32nd",
                        "velocity_curve": "crescendo" # Get louder as you go up
                    }
                }
            ]
        },
        {
            "week": 14,
            "title": "The 'Robert Glasper' Sound",
            "focus": "Modern Jazz Fusion",
            "theory_prompt": "Mixing radiohead-style pedal points with jazz harmony.",
            "exercises": [
                {
                    "id": "ns_wk14_ex1",
                    "name": "Static Melody, Moving Chords",
                    "type": "progression",
                    "instructions": "Keep the top note G constant while playing Cm9 -> Abmaj7 -> Fm9.",
                    "engine_data": {
                        "pedal_tone": 7, # G
                        "chords_underneath": ["Cm", "Ab", "Fm"]
                    }
                }
            ]
        },
        {
            "week": 15,
            "title": "Double-Time Fills",
            "focus": "Rhythmic Excitement",
            "theory_prompt": "Briefly doubling the speed of your playing for a bar.",
            "exercises": [
                {
                    "id": "ns_wk15_ex1",
                    "name": "32nd Note Burst",
                    "type": "rhythm_drill",
                    "instructions": "4 bars of groove, 1 bar of 32nd note arpeggios.",
                    "engine_data": {
                        "pattern": "A-A-A-B",
                        "B_section_density": 32 # Notes per bar
                    }
                }
            ]
        },
        {
            "week": 16,
            "title": "Neo-Soul Capstone",
            "focus": "Performance",
            "theory_prompt": "Combine groove, harmony, and runs into a full loop.",
            "exercises": [
                {
                    "id": "ns_wk16_final",
                    "name": "The Production Loop",
                    "type": "composition",
                    "instructions": "Create a 4-bar loop using: Dilla feel, Tritone Sub, and a Pentatonic Run.",
                    "engine_data": {
                        "requirements": {
                            "swing": 0.6,
                            "harmony": "advanced",
                            "form": "loop"
                        }
                    }
                }
            ]
        }
    ]
}

# Gospel

{
  "id": "gospel_mastery_db_001",
  "meta": {
    "genre": "Gospel",
    "description": "Traditional and Contemporary Gospel Piano. Focuses on triadic upper structures, dominant 7#9 'shout' chords, and specific dynamic swells.",
    "default_bpm": 110,
    "default_swing": 0.60
  },
  "curriculum": [
    {
      "week": 1,
      "module_title": "The Gospel 7th & The Drop-2",
      "pedagogy": {
        "objective": "Move from triads to the rich, open sound of Gospel 7ths.",
        "theory_summary": "Gospel rarely uses close-position triads. We use 'Drop-2' voicings or add the 7th to create a wall of sound."
      },
      "exercises": [
        {
          "id": "gospel_wk1_ex1_diatonic7s",
          "title": "Diatonic 7th Drops",
          "musical_data": {
            "key_center": "C Major",
            "voicing_structure": {
              "description": "LH plays Root-5, RH plays 3-7-9 (Shell Extension)",
              "intervals_lh": [0, 7],
              "intervals_rh": [16, 23, 26],
              "voice_leading_rule": "parallel"
            },
            "midi_events": [
              { "note_offset": 0, "velocity_min": 70, "velocity_max": 90, "duration": 4.0 },
              { "note_offset": 2, "velocity_min": 65, "velocity_max": 85, "duration": 4.0 }
            ],
            "playback_parameters": {
              "articulation": "legato",
              "sustain_pedal": true
            }
          }
        }
      ]
    },
    {
      "week": 2,
      "module_title": "The Preacher's Chord (7#9)",
      "pedagogy": {
        "objective": "Master the Dominant 7#9 for shouts and accents.",
        "theory_summary": "The 7#9 allows for the 'blues' sound within a major key context. It is the backbone of shout music."
      },
      "exercises": [
        {
          "id": "gospel_wk2_ex1_preacher_hits",
          "title": "E7#9 Stabs",
          "musical_data": {
            "key_center": "C Major",
            "voicing_structure": {
              "description": "Dominant 7#9 (The Jimi/Preacher chord)",
              "intervals_absolute": [0, 4, 10, 15], 
              "scale_degrees": ["1", "3", "b7", "#9"]
            },
            "playback_parameters": {
              "velocity_curve": "accent_hard",
              "grid_offset_ms": -10, 
              "swing_percentage": 0.65
            }
          }
        }
      ]
    },
    {
      "week": 5,
      "module_title": "The 7-3-6 Progression",
      "pedagogy": {
        "objective": "Navigate the most important turnaround in Gospel.",
        "theory_summary": "The 7-3-6 uses secondary dominants to pull the ear toward the relative minor (vi)."
      },
      "exercises": [
        {
          "id": "gospel_wk5_ex1_736_progression",
          "title": "7-3-6 in Ab",
          "musical_data": {
            "key_center": "Ab Major",
            "progression_data": [
              {
                "chord_sym": "Gdim7",
                "function": "vii_dim",
                "voicing_stack": [11, 14, 17, 20], 
                "duration": 2
              },
              {
                "chord_sym": "C7alt",
                "function": "III_dom",
                "voicing_stack": [4, 10, 13, 16, 19], 
                "duration": 2
              },
              {
                "chord_sym": "Fm9",
                "function": "vi_min",
                "voicing_stack": [9, 12, 16, 19, 23], 
                "duration": 4
              }
            ],
            "playback_parameters": {
              "rubato_amount": 0.15,
              "velocity_range": [50, 75]
            }
          }
        }
      ]
    },
    {
      "week": 9,
      "module_title": "Advanced Shout Music",
      "pedagogy": {
        "objective": "Develop the stamina and rhythmic precision for high-tempo praise.",
        "theory_summary": "Shout music relies on the 'stride' left hand (1-5 or 1-3-5) against syncopated right-hand rhythmic cells."
      },
      "exercises": [
        {
          "id": "gospel_wk9_ex1_stride_bass",
          "title": "The 1-3-4-b5 Walk Up",
          "musical_data": {
            "tempo_target": 140,
            "key_center": "Bb",
            "lh_pattern": {
              "intervals": [0, 4, 5, 6, 7], 
              "rhythm": "quarter_notes",
              "velocity_accent": "beats_1_3"
            },
            "rh_pattern": {
              "intervals": [10, 14, 17], 
              "rhythm": "syncopated_16ths"
            }
          }
        }
      ]
    },
    {
      "week": 13,
      "module_title": "Talk Music & Atmosphere",
      "pedagogy": {
        "objective": "Provide unobtrusive background support for speakers.",
        "theory_summary": "Talk music avoids standard resolutions. We float between the I and the IV chord using sus2 and sus4 textures."
      },
      "exercises": [
        {
          "id": "gospel_wk13_ex1_floating_sus",
          "title": "The Preacher's Flow",
          "musical_data": {
            "key_center": "Db Major",
            "voicing_structure": {
              "chord_1": "Dbmaj9",
              "chord_2": "Gbmaj9#11",
              "voice_leading": "smooth_semitone"
            },
            "playback_parameters": {
              "velocity_fixed": 45,
              "attack_time": "slow",
              "sustain_pedal": "overlapping"
            }
          }
        }
      ]
    }
  ]
}