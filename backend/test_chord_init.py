import logging
logging.basicConfig(level=logging.INFO)
from app.services.ai.chord_service import chord_service

if chord_service.predictor:
    print("✅ Chord Service Initialized with Predictor")
else:
    print("❌ Chord Service Initialized WITHOUT Predictor")
    
from musiclang_predict import MusicLangPredictor
print("Direct import worked")
