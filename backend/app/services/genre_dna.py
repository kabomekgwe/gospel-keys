"""
Genre DNA Library - Musical characteristics for authentic style generation.

Each genre contains the musical "DNA" that defines its characteristic sound:
- harmonic_movements: Signature chord progressions and movements
- voicing_principles: How chords are voiced in this style  
- rhythm_patterns: Rhythmic feels and patterns
- improvisation_idioms: Common fills, runs, and ornaments
- reference_artists: Master musicians for style context
- avoid: Common pitfalls that make output sound "AI-generated"

This library is used by:
- AIGeneratorService for prompt building
- Genre-specific Arrangers for pattern selection
- Frontend for genre-specific UI hints
"""

from typing import Any


# =============================================================================
# GENRE DNA DEFINITIONS
# =============================================================================

GENRE_DNA: dict[str, dict[str, Any]] = {
    
    # =========================================================================
    # GOSPEL
    # =========================================================================
    "gospel": {
        "name": "Gospel Piano",
        "description": "Rich, emotional, worship-influenced piano style with deep roots in African-American church tradition",
        
        "harmonic_movements": [
            {
                "name": "Plagal Motion (Amen Cadence)",
                "pattern": "IV → I",
                "description": "The quintessential gospel ending - full of resolution and worship",
                "example_key_C": "F → C"
            },
            {
                "name": "Gospel Turnaround",
                "pattern": "I → I7 → IV → ♯IVdim7 → I/V → V7 → I",
                "description": "Classic ending tag that builds and resolves beautifully",
                "example_key_C": "C → C7 → F → F#dim7 → C/G → G7 → C"
            },
            {
                "name": "Classic Shout",
                "pattern": "♭VII → IV → I",
                "description": "Creates that 'shout music' feel - powerful and uplifting",
                "example_key_C": "Bb → F → C"
            },
            {
                "name": "2-5-1 Gospel Style",
                "pattern": "ii7 → V9sus4 → V7(♭9) → Imaj9",
                "description": "Jazz-influenced resolution with gospel extensions",
                "example_key_C": "Dm7 → G9sus4 → G7(b9) → Cmaj9"
            },
            {
                "name": "Borrowed ♭VI",
                "pattern": "♭VImaj7 → ♭VII → I",
                "description": "Modal interchange from parallel minor - creates emotion",
                "example_key_C": "Abmaj7 → Bb → C"
            },
            {
                "name": "Common Tone Diminished",
                "pattern": "I → ♯Idim7 → ii",
                "description": "Chromatic passing chord using diminished",
                "example_key_C": "C → C#dim7 → Dm"
            },
            {
                "name": "Walking Bass Line",
                "pattern": "I → I/3 → IV → ♯IVdim7 → I/5",
                "description": "Ascending bass line under chord changes",
                "example_key_C": "C → C/E → F → F#dim7 → C/G"
            },
        ],
        
        "voicing_principles": [
            "Use close voicings with 2nds for tension (cluster voicings)",
            "Stack 4ths for modern gospel sound (quartal voicings)",
            "Double melody in octaves for power sections",
            "Add 9ths and 13ths liberally - gospel loves extensions",
            "Use sus4 chords that resolve for emotional effect",
            "Left hand: Root + 5th + 10th (or root + 7th + 10th)",
            "Right hand: 3rd, 5th, 7th, 9th in various inversions",
        ],
        
        "rhythm_patterns": [
            "Gospel shuffle (swung 8ths with backbeat emphasis)",
            "Straight 16ths for uptempo praise",
            "Syncopated comping on the 'and' of beats",
            "Stride bass on beats 1 and 3 (slow gospel)",
            "Walking bass for contemporary feel",
        ],
        
        "improvisation_idioms": [
            "Pentatonic runs connecting chord tones",
            "Chromatic approach notes (half-step above/below target)",
            "Gospel 'turns' - melodic ornaments around a note",
            "Call-and-response between hands",
            "Tremolo octaves for intensity building",
            "Grace notes before downbeats",
        ],
        
        "dynamics_and_expression": [
            "Build intensity gradually (verse → chorus → vamp → shout)",
            "Pull back dynamically before the 'drop'",
            "Accents on beats 2 and 4 (backbeat)",
            "Ghost notes for groove (very soft notes)",
            "Ritardando at phrase endings",
        ],
        
        "reference_artists": [
            {"name": "Kirk Franklin", "known_for": "Contemporary gospel, hip-hop fusion, complex extended chords"},
            {"name": "Fred Hammond", "known_for": "Smooth gospel, rich voicings, worship ballads"},
            {"name": "Israel Houghton", "known_for": "Contemporary worship, Latin influences, modern production"},
            {"name": "Cory Henry", "known_for": "Hammond B3 gospel, modern jazz fusion, virtuosic runs"},
            {"name": "Richard Smallwood", "known_for": "Classical gospel, anthem arrangements, choral writing"},
            {"name": "Tye Tribbett", "known_for": "High-energy praise, shouting music, dynamic builds"},
        ],
        
        "avoid": [
            "Equal velocity on all notes (sounds robotic)",
            "Straight 8th notes without shuffle feel",
            "Sparse voicings - gospel is FULL and rich",
            "Starting phrases on beat 1 (anticipate!)",
            "Mechanical repetition without variation",
            "Ignoring the 'conversation' between hands",
        ],
        
        "tempo_ranges": {
            "worship_ballad": (55, 72),
            "contemporary": (80, 100),
            "uptempo": (110, 140),
            "shout": (120, 160),
        },
    },
    
    # =========================================================================
    # JAZZ
    # =========================================================================
    "jazz": {
        "name": "Jazz Piano",
        "description": "Sophisticated harmonic language with swing feel and improvisational freedom",
        
        "harmonic_movements": [
            {
                "name": "ii-V-I",
                "pattern": "ii7 → V7 → Imaj7",
                "description": "The bread and butter of jazz harmony",
                "example_key_C": "Dm7 → G7 → Cmaj7"
            },
            {
                "name": "Tritone Substitution",
                "pattern": "♭II7 → I",
                "description": "Replace V7 with ♭II7 for chromatic bass motion",
                "example_key_C": "Db7 → Cmaj7"
            },
            {
                "name": "Minor ii-V-i",
                "pattern": "iiø7 → V7(♭9) → im7",
                "description": "Minor key resolution with altered dominant",
                "example_key_C": "Dm7b5 → G7(b9) → Cm7"
            },
            {
                "name": "Coltrane Changes",
                "pattern": "Imaj7 → ♭IIImaj7 → Vmaj7 → ♭VIImaj7 → I",
                "description": "Giant Steps-style major third cycle",
                "example_key_C": "Cmaj7 → Ebmaj7 → Gmaj7 → Bbmaj7 → C"
            },
            {
                "name": "Backdoor ii-V",
                "pattern": "iv7 → ♭VII7 → Imaj7",
                "description": "Approach from minor subdominant side",
                "example_key_C": "Fm7 → Bb7 → Cmaj7"
            },
            {
                "name": "Rhythm Changes Bridge",
                "pattern": "III7 → VI7 → II7 → V7",
                "description": "Classic bridge from 'I Got Rhythm'",
                "example_key_C": "E7 → A7 → D7 → G7"
            },
        ],
        
        "voicing_principles": [
            "Rootless left-hand voicings (3-7. or 7-3 shells)",
            "Drop 2 voicings for full but clear sound",
            "Shell voicings (root + 3rd + 7th)",
            "Block chords for melody harmonization",
            "Quartal voicings for modal jazz",
            "Avoid root in left hand for combo playing",
        ],
        
        "rhythm_patterns": [
            "Swing 8ths (triplet-based feel)",
            "Comping rhythms (Charleston, 3+3+2)",
            "Straight 8ths for Latin/Bossa",
            "Walking bass lines (for solo piano)",
        ],
        
        "improvisation_idioms": [
            "Bebop scales (adding chromatic passing tones)",
            "Enclosures around target notes",
            "Approach patterns (chromatic, diatonic)",
            "Digital patterns (1235, etc.)",
            "Quotes and motif development",
        ],
        
        "reference_artists": [
            {"name": "Bill Evans", "known_for": "Impressionist harmony, introspective playing, rootless voicings"},
            {"name": "Oscar Peterson", "known_for": "Virtuosic technique, powerful swing, stride influence"},
            {"name": "Herbie Hancock", "known_for": "Modal jazz, funk fusion, innovative voicings"},
            {"name": "Bud Powell", "known_for": "Bebop vocabulary, linear right hand, sparse left hand"},
            {"name": "Ahmad Jamal", "known_for": "Space and dynamics, rhythmic innovation, trio interplay"},
            {"name": "Chick Corea", "known_for": "Latin jazz, Spanish tinge, bright voicings"},
        ],
        
        "avoid": [
            "Root-position voicings (too heavy for jazz)",
            "Straight 8th notes in swing contexts",
            "Parallel octaves/5ths in voice leading",
            "Over-busy comping (leave space)",
            "Ignoring the form structure",
        ],
        
        "tempo_ranges": {
            "ballad": (50, 70),
            "medium_swing": (100, 140),
            "uptempo": (160, 280),
            "latin": (100, 140),
        },
    },
    
    # =========================================================================
    # NEO-SOUL
    # =========================================================================
    "neo_soul": {
        "name": "Neo-Soul/R&B Piano",
        "description": "Smooth, groove-based style blending jazz harmony with R&B rhythms",
        
        "harmonic_movements": [
            {
                "name": "Smooth ii-V-I",
                "pattern": "ii9 → V13 → Imaj9",
                "description": "Jazz progression with R&B extensions",
                "example_key_C": "Dm9 → G13 → Cmaj9"
            },
            {
                "name": "Minor 7th Vamp",
                "pattern": "im9 → iv9 → im9",
                "description": "Hypnotic minor groove",
                "example_key_C": "Cm9 → Fm9 → Cm9"
            },
            {
                "name": "Erykah Special",
                "pattern": "Imaj7 → ♯IVm7(♭5) → IV → ♯IVdim7",
                "description": "That Erykah Badu chromatic ascent",
                "example_key_C": "Cmaj7 → F#m7b5 → Fmaj7 → F#dim7"
            },
            {
                "name": "D'Angelo Float",
                "pattern": "im11 → ♭VIImaj9 → ♭VImaj9",
                "description": "Dreamy modal interchange loop",
                "example_key_C": "Cm11 → Bbmaj9 → Abmaj9"
            },
        ],
        
        "voicing_principles": [
            "Rich 9th, 11th, and 13th extensions",
            "Suspended chords that don't resolve",
            "Major 7th chords on minor roots (maj7#5)",
            "Stacked 4ths for ethereal sound",
            "Rhodes/EP-style voicings (wide intervals in left hand)",
        ],
        
        "rhythm_patterns": [
            "Laid-back 16th note grooves",
            "Behind-the-beat feel (slightly late)",
            "Syncopated funk patterns",
            "Gospel-influenced backbeat",
        ],
        
        "reference_artists": [
            {"name": "Robert Glasper", "known_for": "Jazz-hip hop fusion, modern voicings, experimentation"},
            {"name": "D'Angelo", "known_for": "Laid-back grooves, vintage soul, behind-the-beat feel"},
            {"name": "Erykah Badu", "known_for": "Quirky harmony, jazz influence, spiritual depth"},
            {"name": "Kiefer", "known_for": "Beat-driven jazz, lo-fi aesthetic, left-field harmony"},
            {"name": "James Poyser", "known_for": "Roots production, warm Rhodes sounds, sophisticated R&B"},
        ],
        
        "avoid": [
            "Overly busy playing (neo-soul breathes)",
            "Harsh attacks (should be smooth and warm)",
            "Standard jazz voicings without extensions",
            "Ignoring the groove (the pocket is everything)",
        ],
        
        "tempo_ranges": {
            "slow_groove": (60, 80),
            "medium": (85, 105),
            "uptempo": (110, 130),
        },
    },
    
    # =========================================================================
    # BLUES
    # =========================================================================
    "blues": {
        "name": "Blues Piano",
        "description": "Gritty, expressive style rooted in the 12-bar blues tradition",
        
        "harmonic_movements": [
            {
                "name": "12-Bar Blues",
                "pattern": "I7 | I7 | I7 | I7 | IV7 | IV7 | I7 | I7 | V7 | IV7 | I7 | V7",
                "description": "The fundamental blues form",
                "example_key_C": "C7 x4 | F7 x2 | C7 x2 | G7 | F7 | C7 | G7"
            },
            {
                "name": "Quick Change",
                "pattern": "I7 | IV7 | I7 | I7 | ...",
                "description": "Moves to IV in measure 2",
                "example_key_C": "C7 | F7 | C7 | C7 | ..."
            },
            {
                "name": "Jazz Blues",
                "pattern": "I7 | IV7 | I7 | ♯I°7 | ii7 | V7 | I7 | vi7 | ii7 | V7 | I7 | V7",
                "description": "Blues with jazz substitutions",
                "example_key_C": "C7 | F7 | C7 | C#dim7 | Dm7 | G7 | ..."
            },
        ],
        
        "voicing_principles": [
            "Dominant 7th on EVERY chord by default",
            "Blues scale notes as color tones (♭3, ♭5, ♭7)",
            "Boogie-woogie left hand patterns",
            "Grace notes and crushed notes",
            "Tremolo for intensity",
        ],
        
        "rhythm_patterns": [
            "Shuffle feel (swung triplet-based)",
            "Boogie-woogie left hand (8-to-the-bar)",
            "Slow blues drag (behind the beat)",
            "Stop-time for dramatic effect",
        ],
        
        "improvisation_idioms": [
            "Blues scale licks",
            "Call-and-response with the melody",
            "Crushed notes (grace notes into chord tones)",
            "Trills and tremolo",
            "Bent notes (grace note slide into pitch)",
        ],
        
        "reference_artists": [
            {"name": "Ray Charles", "known_for": "Gospel-blues fusion, soul piano, expressiveness"},
            {"name": "Oscar Peterson", "known_for": "Blues-jazz synthesis, virtuosic technique"},
            {"name": "Pinetop Perkins", "known_for": "Chicago blues, boogie-woogie, authentic Delta style"},
            {"name": "Dr. John", "known_for": "New Orleans blues, funk influence, rhythmic complexity"},
            {"name": "Otis Spann", "known_for": "Deep blues feeling, Muddy Waters band, emotional depth"},
        ],
        
        "avoid": [
            "Clean, polished sound (blues is raw)",
            "Major 7th chords (too pretty for blues)",
            "Even dynamics (blues is expressive)",
            "Ignoring the shuffle feel",
        ],
        
        "tempo_ranges": {
            "slow_blues": (50, 70),
            "medium_shuffle": (90, 120),
            "uptempo": (130, 180),
            "boogie": (140, 200),
        },
    },
    
    # =========================================================================
    # CLASSICAL
    # =========================================================================
    "classical": {
        "name": "Classical Piano",
        "description": "Western classical tradition with formal harmonic language and precise notation",
        
        "harmonic_movements": [
            {
                "name": "Authentic Cadence",
                "pattern": "V → I",
                "description": "The strongest classical resolution"
            },
            {
                "name": "Deceptive Cadence",
                "pattern": "V → vi",
                "description": "Surprise resolution for continuation"
            },
            {
                "name": "Romantic Chain",
                "pattern": "I → vi → IV → ii → V → I",
                "description": "Circle of fifths with diatonic substitutions"
            },
            {
                "name": "Neapolitan",
                "pattern": "♭II6 → V → I",
                "description": "Flat-II chord in first inversion before cadence"
            },
        ],
        
        "voicing_principles": [
            "Voice leading rules (no parallel 5ths/8ves)",
            "Proper bass motion (contrary to melody when possible)",
            "Correct doubling (root or 5th in triads)",
            "Register-appropriate textures",
        ],
        
        "reference_artists": [
            {"name": "Chopin", "known_for": "Romantic harmony, rubato, poetic expression"},
            {"name": "Debussy", "known_for": "Impressionism, whole tone/pentatonic colors, pedal"},
            {"name": "Bach", "known_for": "Counterpoint, voice independence, perfect form"},
            {"name": "Rachmaninoff", "known_for": "Lush harmony, virtuosic technique, emotional depth"},
        ],
        
        "avoid": [
            "Parallel 5ths and octaves (voice leading rule)",
            "Jazz extensions in Baroque/Classical contexts",
            "Ignoring period-appropriate style",
        ],
        
        "tempo_ranges": {
            "largo": (40, 60),
            "adagio": (66, 76),
            "andante": (76, 108),
            "allegro": (120, 168),
            "presto": (168, 200),
        },
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_genre_dna(genre: str) -> dict[str, Any] | None:
    """Get the DNA for a specific genre."""
    return GENRE_DNA.get(genre.lower())


def get_genre_prompt_context(genre: str) -> str:
    """
    Build a prompt context string from genre DNA.
    
    This is injected into AI prompts to guide authentic generation.
    """
    dna = get_genre_dna(genre)
    if not dna:
        return ""
    
    # Build structured context
    sections = [
        f"=== {dna['name'].upper()} STYLE GUIDE ===",
        f"\n{dna['description']}",
    ]
    
    # Harmonic movements
    if dna.get("harmonic_movements"):
        sections.append("\nCHARACTERISTIC PROGRESSIONS:")
        for movement in dna["harmonic_movements"][:4]:  # Top 4
            sections.append(f"• {movement['name']}: {movement['pattern']}")
            if "description" in movement:
                sections.append(f"  ({movement['description']})")
    
    # Voicing principles
    if dna.get("voicing_principles"):
        sections.append("\nVOICING PRINCIPLES:")
        for principle in dna["voicing_principles"][:4]:
            sections.append(f"• {principle}")
    
    # What to avoid
    if dna.get("avoid"):
        sections.append("\n⚠️ AVOID (common AI mistakes):")
        for item in dna["avoid"]:
            sections.append(f"• {item}")
    
    # Reference artists
    if dna.get("reference_artists"):
        artists = [a["name"] for a in dna["reference_artists"][:3]]
        sections.append(f"\nCHANNEL THE SPIRIT OF: {', '.join(artists)}")
    
    return "\n".join(sections)


def get_genre_voicing_principles(genre: str) -> list[str]:
    """Get voicing principles for a genre."""
    dna = get_genre_dna(genre)
    return dna.get("voicing_principles", []) if dna else []


def get_genre_avoid_list(genre: str) -> list[str]:
    """Get list of things to avoid for a genre."""
    dna = get_genre_dna(genre)
    return dna.get("avoid", []) if dna else []


def get_genre_reference_artists(genre: str) -> list[dict[str, str]]:
    """Get reference artists for a genre."""
    dna = get_genre_dna(genre)
    return dna.get("reference_artists", []) if dna else []


def get_tempo_range(genre: str, application: str) -> tuple[int, int]:
    """Get tempo range for a genre and application type."""
    dna = get_genre_dna(genre)
    if not dna:
        return (80, 120)  # Default
    
    tempo_ranges = dna.get("tempo_ranges", {})
    
    # Try exact match first
    if application in tempo_ranges:
        return tempo_ranges[application]
    
    # Try fuzzy match
    for key, value in tempo_ranges.items():
        if application.lower() in key.lower() or key.lower() in application.lower():
            return value
    
    # Return first available or default
    if tempo_ranges:
        return list(tempo_ranges.values())[0]
    return (80, 120)


def get_creativity_instruction(creativity_level: str) -> str:
    """
    Get prompt instruction based on creativity level.
    
    Args:
        creativity_level: One of "conservative", "balanced", "adventurous", "experimental"
    
    Returns:
        Instruction string to inject into AI prompt
    """
    instructions = {
        "conservative": """
CREATIVITY: CONSERVATIVE
Stay within established patterns for this genre. Use proven, idiomatic choices.
The output should sound like a textbook example of this style.
""",
        "balanced": """
CREATIVITY: BALANCED
Mix familiar patterns with some fresh ideas. Use the idiom as a foundation
but add personal touches. Aim for something both authentic and interesting.
""",
        "adventurous": """
CREATIVITY: ADVENTUROUS  
Push boundaries while staying musical. Use unexpected but justified choices.
Surprise the listener with fresh harmonic turns, but resolve satisfyingly.
""",
        "experimental": """
CREATIVITY: EXPERIMENTAL
Think outside the box. Blend influences from other genres, use unconventional
voicings, and create something that challenges expectations. Be bold!
""",
    }
    return instructions.get(creativity_level.lower(), instructions["balanced"])


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "GENRE_DNA",
    "get_genre_dna",
    "get_genre_prompt_context",
    "get_genre_voicing_principles",
    "get_genre_avoid_list", 
    "get_genre_reference_artists",
    "get_tempo_range",
    "get_creativity_instruction",
]
