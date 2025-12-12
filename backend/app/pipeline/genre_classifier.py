"""
Genre Detection and Classification

Uses audio features to classify piano music into genres:
- Gospel
- Jazz  
- Blues
- Classical
- Contemporary
"""

from typing import Dict, List, Tuple
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import librosa
from pathlib import Path


# Pre-defined genre characteristics
GENRE_CHARACTERISTICS = {
    "gospel": {
        "typical_tempo_range": (70, 140),
        "common_progressions": ["I-IV-V", "ii-V-I", "I-vi-IV-V"],
        "harmonic_complexity": "moderate",
        "rhythmic_patterns": ["syncopation", "swing"],
        "chord_extensions": ["7th", "9th", "add9"]
    },
    "jazz": {
        "typical_tempo_range": (100, 200),
        "common_progressions": ["ii-V-I", "I-VI-ii-V", "blues"],
        "harmonic_complexity": "high",
        "rhythmic_patterns": ["swing", "bebop", "complex_syncopation"],
        "chord_extensions": ["9th", "11th", "13th", "altered"]
    },
    "blues": {
        "typical_tempo_range": (60, 120),
        "common_progressions": ["12-bar blues", "8-bar blues"],
        "harmonic_complexity": "low-moderate",
        "rhythmic_patterns": ["shuffle", "straight"],
        "chord_extensions": ["7th", "9th"]
    },
    "classical": {
        "typical_tempo_range": (40, 180),
        "common_progressions": ["I-IV-V-I", "circle_of_fifths"],
        "harmonic_complexity": "variable",
        "rhythmic_patterns": ["strict_time", "rubato"],
        "chord_extensions": ["triads", "7th"]
    },
    "contemporary": {
        "typical_tempo_range": (80, 140),
        "common_progressions": ["I-V-vi-IV", "vi-IV-I-V"],
        "harmonic_complexity": "moderate",
        "rhythmic_patterns": ["straight", "modern"],
        "chord_extensions": ["7th", "add9", "sus2", "sus4"]
    }
}


def extract_genre_features(audio_path: Path) -> Dict:
    """
    Extract audio features for genre classification
    
    Args:
        audio_path: Path to audio file
    
    Returns:
        Dictionary of features
    """
    # Load audio
    y, sr = librosa.load(str(audio_path), sr=22050)
    
    # Tempo and rhythm
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    
    # Spectral features
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    
    # Chroma features (harmony)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    
    # MFCC (timbre)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    
    # Zero crossing rate (brightness)
    zcr = librosa.feature.zero_crossing_rate(y)
    
    # Rhythmic regularity (via tempogram)
    tempogram = librosa.feature.tempogram(y=y, sr=sr)
    
    features = {
        # Tempo features
        "tempo": float(tempo),
        "beat_strength": float(np.mean(librosa.onset.onset_strength(y=y, sr=sr))),
        
        # Spectral features
        "spectral_centroid_mean": float(np.mean(spectral_centroids)),
        "spectral_centroid_std": float(np.std(spectral_centroids)),
        "spectral_rolloff_mean": float(np.mean(spectral_rolloff)),
        
        # Harmonic features
        "chroma_mean": chroma.mean(axis=1).tolist(),
        "chroma_std": chroma.std(axis=1).tolist(),
        "harmonic_complexity": float(np.std(chroma)),
        
        # Timbre features
        "mfcc_mean": mfcc.mean(axis=1).tolist(),
        "mfcc_std": mfcc.std(axis=1).tolist(),
        
        # Rhythm features
        "zero_crossing_rate_mean": float(np.mean(zcr)),
        "rhythmic_regularity": float(np.std(tempogram)),
    }
    
    return features


def classify_genre_rule_based(features: Dict, chords: List[Dict]) -> Dict:
    """
    Rule-based genre classification
    
    Uses heuristics based on tempo, harmony, and progressions.
    
    Args:
        features: Audio features from extract_genre_features
        chords: Chord progression from transcription
    
    Returns:
        Genre probabilities
    """
    scores = {genre: 0.0 for genre in GENRE_CHARACTERISTICS.keys()}
    
    tempo = features["tempo"]
    harmonic_complexity = features["harmonic_complexity"]
    
    # Tempo-based scoring
    for genre, chars in GENRE_CHARACTERISTICS.items():
        min_tempo, max_tempo = chars["typical_tempo_range"]
        if min_tempo <= tempo <= max_tempo:
            scores[genre] += 0.3
    
    # Harmonic complexity scoring
    if harmonic_complexity > 1.5:  # High complexity
        scores["jazz"] += 0.4
        scores["gospel"] += 0.2
    elif harmonic_complexity < 0.8:  # Low complexity
        scores["blues"] += 0.3
        scores["classical"] += 0.2
    
    # Chord progression analysis (simplified)
    if len(chords) > 4:
        # Check for jazz patterns (many 7ths, 9ths)
        extended_chords = sum(1 for c in chords if '7' in c.get('quality', '') or '9' in c.get('quality', ''))
        jazz_ratio = extended_chords / len(chords)
        
        if jazz_ratio > 0.7:
            scores["jazz"] += 0.5
        elif jazz_ratio > 0.4:
            scores["gospel"] += 0.3
    
    # Normalize to probabilities
    total = sum(scores.values())
    if total > 0:
        scores = {k: v/total for k, v in scores.items()}
    
    # Get top genre
    top_genre = max(scores.items(), key=lambda x: x[1])
    
    return {
        "primary_genre": top_genre[0],
        "confidence": top_genre[1],
        "all_probabilities": scores,
        "method": "rule_based"
    }


def detect_subgenre_jazz(features: Dict, chords: List[Dict]) -> List[str]:
    """
    Detect jazz subgenres
    
    - Bebop: Fast tempo (>180), complex harmony
    - Cool jazz: Medium tempo, smooth
    - Hard bop: Medium-fast, bluesy
    - Stride: Specific left-hand pattern
    """
    subgenres = []
    tempo = features["tempo"]
    
    if tempo > 180:
        subgenres.append("bebop")
    elif 100 < tempo < 140:
        if features["harmonic_complexity"] < 1.0:
            subgenres.append("cool jazz")
        else:
            subgenres.append("hard bop")
    
    # Check for stride pattern (future: analyze bass line)
    # subgenres.append("stride")
    
    return subgenres if subgenres else ["modern jazz"]


def detect_subgenre_gospel(features: Dict, chords: List[Dict]) -> List[str]:
    """
    Detect gospel subgenres
    
    - Traditional: Slower, simpler harmony
    - Contemporary: Faster, extended chords
    - Urban gospel: Modern production style
    """
    subgenres = []
    tempo = features["tempo"]
    harmonic_complexity = features["harmonic_complexity"]
    
    if tempo < 80 and harmonic_complexity < 1.0:
        subgenres.append("traditional gospel")
    elif tempo > 110 and harmonic_complexity > 1.2:
        subgenres.append("contemporary gospel")
    else:
        subgenres.append("urban gospel")
    
    return subgenres


def analyze_genre(audio_path: Path, chords: List[Dict]) -> Dict:
    """
    Complete genre analysis
    
    Args:
        audio_path: Path to audio file
        chords: Chord progression from transcription
    
    Returns:
        Complete genre analysis
    """
    # Extract features
    features = extract_genre_features(audio_path)
    
    # Classify genre
    classification = classify_genre_rule_based(features, chords)
    
    # Detect subgenres based on primary genre
    subgenres = []
    if classification["primary_genre"] == "jazz":
        subgenres = detect_subgenre_jazz(features, chords)
    elif classification["primary_genre"] == "gospel":
        subgenres = detect_subgenre_gospel(features, chords)
    
    return {
        **classification,
        "subgenres": subgenres,
        "characteristics": GENRE_CHARACTERISTICS[classification["primary_genre"]],
        "tempo": features["tempo"],
        "harmonic_complexity_score": features["harmonic_complexity"]
    }
