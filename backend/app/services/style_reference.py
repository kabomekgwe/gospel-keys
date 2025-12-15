"""
Style Reference Service

Maps artist names and track references to musical characteristics
for more targeted AI generation.

Users can say "like Kirk Franklin" or "channel Bill Evans" and the AI
will incorporate those artists' characteristic styles into generation.
"""

from typing import Optional


# =============================================================================
# ARTIST STYLE DATABASE
# =============================================================================

ARTIST_STYLES: dict[str, dict] = {
    
    # =========================================================================
    # GOSPEL ARTISTS
    # =========================================================================
    
    "kirk_franklin": {
        "name": "Kirk Franklin",
        "genre": "gospel",
        "era": "contemporary",
        "characteristics": [
            "Contemporary gospel with hip-hop and R&B influences",
            "Complex extended chords (maj9, 13, sus4, add9)",
            "Strong rhythmic emphasis on 2 and 4 (backbeat)",
            "Call-and-response patterns between instruments and choir",
            "Dramatic dynamic builds leading to 'shout' sections",
            "Funky bass lines and modern production",
        ],
        "signature_progressions": [
            "I → I7/V → IV → ♯IVdim7 → I",
            "♭VImaj7 → ♭VII → I",
            "ii9 → V13 → Imaj9",
        ],
        "voicing_style": "Dense, close position with extensions. Lots of 9ths and 13ths. Modern gospel stack voicings.",
        "rhythm_style": "Gospel shuffle with contemporary R&B feel. Syncopated comping.",
        "tempo_preference": (90, 140),
        "notable_songs": ["Melodies from Heaven", "Stomp", "I Smile", "Love Theory"],
    },
    
    "fred_hammond": {
        "name": "Fred Hammond",
        "genre": "gospel",
        "era": "contemporary",
        "characteristics": [
            "Smooth, sophisticated gospel with jazz influences",
            "Rich extended chord voicings",
            "Worship ballad specialty",
            "Bass-driven arrangements (as a bassist himself)",
            "Silky melodic lines",
        ],
        "signature_progressions": [
            "Imaj9 → vi7 → IVmaj9 → V11",
            "ii9 → V13sus4 → Imaj9",
        ],
        "voicing_style": "Warm, rich voicings with careful voice leading. Gospel-jazz fusion approach.",
        "rhythm_style": "Laid-back groove. Smooth R&B influenced gospel.",
        "tempo_preference": (70, 110),
        "notable_songs": ["No Weapon", "Blessed", "Let the Praise Begin"],
    },
    
    "israel_houghton": {
        "name": "Israel Houghton",
        "genre": "gospel",
        "era": "contemporary",
        "characteristics": [
            "Contemporary worship with Latin influences",
            "Gospel-rock-Latin fusion",
            "Energetic, uplifting praise songs",
            "World music textures",
            "Modern production with live band feel",
        ],
        "signature_progressions": [
            "I → V/VII → vi → IV",
            "I → III7 → vi → IV",
        ],
        "voicing_style": "Open voicings with octave doubling. Guitar-influenced piano parts.",
        "rhythm_style": "Latin-influenced grooves. Syncopated patterns.",
        "tempo_preference": (100, 150),
        "notable_songs": ["Friend of God", "I Am Not Forgotten", "Alpha & Omega"],
    },
    
    "cory_henry": {
        "name": "Cory Henry",
        "genre": "gospel",
        "era": "contemporary",
        "characteristics": [
            "Virtuosic organ and piano technique",
            "Gospel-jazz fusion at the highest level",
            "Extended improvisation",
            "Snarky Puppy influence",
            "Hammond B3 gospel tradition",
        ],
        "signature_progressions": [
            "Modal interchange progressions",
            "Coltrane-influenced substitutions in gospel context",
        ],
        "voicing_style": "Advanced jazz voicings in gospel context. Quartal stacks. Complex extensions.",
        "rhythm_style": "Polyrhythmic, complex grooves. Jazz-influenced timing.",
        "tempo_preference": (80, 180),
        "notable_songs": ["Art of Love", "In the Water"],
    },
    
    # =========================================================================
    # JAZZ ARTISTS
    # =========================================================================
    
    "bill_evans": {
        "name": "Bill Evans",
        "genre": "jazz",
        "era": "1960s-1980s",
        "characteristics": [
            "Impressionistic harmony influenced by Debussy/Ravel",
            "Introspective, lyrical playing",
            "Innovative rootless left-hand voicings",
            "Trio interplay and conversational dynamics",
            "Rubato and expressive timing",
        ],
        "signature_progressions": [
            "Modal interchange progressions",
            "Romantically extended ii-V-I chains",
        ],
        "voicing_style": "Rootless left-hand voicings (3-5-7-9 or 7-9-3-5). Block chord melodies. Close-voiced stacks.",
        "rhythm_style": "Gentle swing. Behind-the-beat feel. Rubato phrasing.",
        "tempo_preference": (50, 140),
        "notable_songs": ["Peace Piece", "Waltz for Debby", "Blue in Green"],
    },
    
    "oscar_peterson": {
        "name": "Oscar Peterson",
        "genre": "jazz",
        "era": "1950s-2000s",
        "characteristics": [
            "Virtuosic technique and speed",
            "Powerful, full sound",
            "Stride piano influence",
            "Blues feeling in jazz context",
            "Swagger and confidence",
        ],
        "signature_progressions": [
            "Blues-influenced jazz progressions",
            "Standard ii-V-I with blues coloring",
        ],
        "voicing_style": "Full, powerful voicings. Stride bass. Block chords at speed.",
        "rhythm_style": "Driving swing. Strong time feel. Uptempo specialty.",
        "tempo_preference": (100, 280),
        "notable_songs": ["C Jam Blues", "Hymn to Freedom"],
    },
    
    "herbie_hancock": {
        "name": "Herbie Hancock",
        "genre": "jazz",
        "era": "1960s-present",
        "characteristics": [
            "Modal jazz innovations",
            "Funk and electronic fusion",
            "Reinvention across decades",
            "Quartal voicings and modern harmony",
            "Rhythmic complexity",
        ],
        "signature_progressions": [
            "Modal vamps",
            "Unusual extensions and alterations",
        ],
        "voicing_style": "Quartal voicings. So What voicings. Modern extensions. Space and silence.",
        "rhythm_style": "Funky and rhythmic. Syncopated comping. Groove-oriented.",
        "tempo_preference": (80, 200),
        "notable_songs": ["Maiden Voyage", "Cantaloupe Island", "Watermelon Man"],
    },
    
    "ahmad_jamal": {
        "name": "Ahmad Jamal",
        "genre": "jazz",
        "era": "1950s-present",
        "characteristics": [
            "Masterful use of space and silence",
            "Dynamics and drama",
            "Rhythmic innovation",
            "Influenced Miles Davis",
            "Trio interplay",
        ],
        "signature_progressions": [
            "Creative reharmonizations of standards",
        ],
        "voicing_style": "Sparse, effective voicings. Masterful use of silence. Less is more.",
        "rhythm_style": "Innovative rhythmic approach. Surprising accents. Space.",
        "tempo_preference": (80, 180),
        "notable_songs": ["Poinciana", "But Not for Me"],
    },
    
    "chick_corea": {
        "name": "Chick Corea",
        "genre": "jazz",
        "era": "1960s-2020s",
        "characteristics": [
            "Latin jazz influence",
            "Spanish tinge and flamenco colors",
            "Return to Forever fusion",
            "Classical-jazz synthesis",
            "Bright, crystalline tone",
        ],
        "signature_progressions": [
            "Spanish-influenced progressions",
            "Modal jazz with Latin flavor",
        ],
        "voicing_style": "Bright, clear voicings. Spanish colors. Latin montunos.",
        "rhythm_style": "Latin jazz rhythms. Montunos. Salsa influence.",
        "tempo_preference": (100, 220),
        "notable_songs": ["Spain", "La Fiesta", "Crystal Silence"],
    },
    
    # =========================================================================
    # NEO-SOUL/R&B ARTISTS
    # =========================================================================
    
    "robert_glasper": {
        "name": "Robert Glasper",
        "genre": "neo_soul",
        "era": "2000s-present",
        "characteristics": [
            "Jazz-hip hop fusion pioneer",
            "Modern voicings with hip-hop sensibility",
            "Experimentation with form and texture",
            "R&B melodic approach with jazz harmony",
        ],
        "signature_progressions": [
            "Extended minor vamps",
            "Gospel-influenced progressions in R&B context",
        ],
        "voicing_style": "Rich extensions. Rhodes-influenced. Modern jazz-hiphop hybrid voicings.",
        "rhythm_style": "Hip-hop influenced grooves. J Dilla pocket. Behind the beat.",
        "tempo_preference": (70, 100),
        "notable_songs": ["Afro Blue", "F.T.B."],
    },
    
    "dangelo": {
        "name": "D'Angelo",
        "genre": "neo_soul", 
        "era": "1990s-present",
        "characteristics": [
            "Classic soul revival with modern edge",
            "Laid-back, behind-the-beat grooves",
            "Prince influence with more warmth",
            "Live band feel with studio perfection",
        ],
        "signature_progressions": [
            "Minor 9th vamps",
            "Erykah-style chromatic movements",
        ],
        "voicing_style": "Warm, vintage Rhodes voicings. Rich but not over-stacked. Soul-influenced.",
        "rhythm_style": "Way behind the beat. Lazy, hypnotic groove. Drum machine meets live drums.",
        "tempo_preference": (60, 95),
        "notable_songs": ["Untitled (How Does It Feel)", "Really Love"],
    },
    
    "erykah_badu": {
        "name": "Erykah Badu",
        "genre": "neo_soul",
        "era": "1990s-present", 
        "characteristics": [
            "Quirky, unconventional harmony",
            "Strong jazz and hip-hop influence",
            "Spiritual and introspective",
            "Afrofuturist aesthetic",
        ],
        "signature_progressions": [
            "Imaj7 → ♯IVm7(♭5) → IVmaj7 → ♯IVdim7",
            "Modal vamps with unexpected turns",
        ],
        "voicing_style": "Unique, unexpected voicings. Wide intervals. Questioning harmonic choices.",
        "rhythm_style": "J Dilla-influenced pocket. Hip-hop grooves. Off-kilter timing.",
        "tempo_preference": (70, 100),
        "notable_songs": ["On & On", "Tyrone", "Didn't Cha Know"],
    },
    
    # =========================================================================
    # BLUES ARTISTS
    # =========================================================================
    
    "ray_charles": {
        "name": "Ray Charles",
        "genre": "blues",
        "era": "1950s-2000s",
        "characteristics": [
            "Gospel-blues-soul fusion pioneer",
            "Emotional, soulful expressiveness",
            "R&B originator",
            "Versatility across genres",
        ],
        "signature_progressions": [
            "Gospel turnarounds in blues context",
            "Soul-influenced blues changes",
        ],
        "voicing_style": "Soul-influenced blues voicings. Gospel touches. Simple but effective.",
        "rhythm_style": "Swinging, soulful feel. Gospel-influenced rhythms.",
        "tempo_preference": (70, 140),
        "notable_songs": ["What'd I Say", "Georgia on My Mind", "Hit the Road Jack"],
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_artist_style(artist_name: str) -> Optional[dict]:
    """
    Get style information for an artist.
    
    Args:
        artist_name: Artist name (case insensitive, spaces become underscores)
    
    Returns:
        Artist style dict or None if not found
    """
    # Normalize the artist name
    normalized = artist_name.lower().replace(" ", "_").replace("-", "_")
    
    # Direct match
    if normalized in ARTIST_STYLES:
        return ARTIST_STYLES[normalized]
    
    # Partial match (if user says "Kirk" instead of "Kirk Franklin")
    for key, value in ARTIST_STYLES.items():
        if normalized in key or key.startswith(normalized):
            return value
    
    return None


def get_style_reference_prompt(artist_or_track: str) -> str:
    """
    Build a prompt addition for style reference.
    
    This is injected into AI prompts when user provides a style reference.
    
    Args:
        artist_or_track: Artist name or track reference
    
    Returns:
        Prompt string to add to generation request
    """
    style = get_artist_style(artist_or_track)
    
    if not style:
        return f"""
STYLE REFERENCE: {artist_or_track}
(Note: This artist is not in our database, but channel their musical spirit
based on your knowledge of their work.)
"""
    
    # Build comprehensive prompt
    characteristics = "\n".join(f"  • {c}" for c in style["characteristics"])
    progressions = "\n".join(f"  • {p}" for p in style.get("signature_progressions", []))
    
    return f"""
═══════════════════════════════════════════════════════════
STYLE REFERENCE: {style['name']} ({style['genre'].upper()})
═══════════════════════════════════════════════════════════

MUSICAL DNA:
{characteristics}

VOICING APPROACH:
  {style.get('voicing_style', 'Standard for genre')}

RHYTHM STYLE:
  {style.get('rhythm_style', 'Standard for genre')}

SIGNATURE PROGRESSIONS:
{progressions}

NOTABLE SONGS FOR REFERENCE:
  {', '.join(style.get('notable_songs', []))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPORTANT: Channel {style['name']}'s musical spirit! 
Create something that FEELS like their work but is ORIGINAL.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""


def get_artists_for_genre(genre: str) -> list[dict]:
    """
    Get all artists in a specific genre.
    
    Args:
        genre: Genre name
    
    Returns:
        List of artist style dicts
    """
    return [
        artist for artist in ARTIST_STYLES.values()
        if artist["genre"].lower() == genre.lower()
    ]


def search_artists(query: str) -> list[dict]:
    """
    Search for artists by name or characteristics.
    
    Args:
        query: Search query
    
    Returns:
        List of matching artist style dicts
    """
    query_lower = query.lower()
    matches = []
    
    for key, artist in ARTIST_STYLES.items():
        # Check name
        if query_lower in artist["name"].lower():
            matches.append(artist)
            continue
        
        # Check characteristics
        for char in artist.get("characteristics", []):
            if query_lower in char.lower():
                matches.append(artist)
                break
    
    return matches


def list_all_artists() -> list[str]:
    """Get list of all available artist names."""
    return [artist["name"] for artist in ARTIST_STYLES.values()]


# =============================================================================
# EXPORTS  
# =============================================================================

__all__ = [
    "ARTIST_STYLES",
    "get_artist_style",
    "get_style_reference_prompt",
    "get_artists_for_genre",
    "search_artists",
    "list_all_artists",
]
