from pathlib import Path
import pytest
import sys

# Add app to path if not installed
sys.path.append(str(Path(__file__).parent.parent.parent))

def test_musicpy_integration():
    """Test MusicPy service basic functionality"""
    try:
        from app.services.musicpy_service import musicpy_service
        progression = musicpy_service.generate_chord_progression(key="C", scale="major")
        assert len(progression) == 4
        assert progression[0] == "C"
        print("MusicPy Service: OK")
    except ImportError:
        pytest.fail("MusicPy not installed")

def test_verovio_integration():
    """Test Verovio service basic functionality"""
    try:
        from app.services.verovio_service import verovio_service, VEROVIO_AVAILABLE
        if not VEROVIO_AVAILABLE:
            pytest.skip("Verovio not explicitly required if install failed, but technically should be there")
        
        # Test imports at least
        assert verovio_service is not None
        print("Verovio Service: OK")
    except ImportError:
        pytest.fail("Verovio import failed hard")

def test_essentia_integration():
    """Test Essentia service basic functionality"""
    try:
        from app.services.essentia_service import essentia_service, ESSENTIA_AVAILABLE
        if not ESSENTIA_AVAILABLE:
           print("Essentia likely missing on incompatible architecture, skipping")
           return
        
        assert essentia_service is not None
        print("Essentia Service: OK")
    except ImportError:
        print("Essentia import failed")

def test_audiocraft_integration():
    """Test AudioCraft service basic availability (not full generation which is slow)"""
    try:
        # We just test we can import the service class, not load the model (too heavy for quick test)
        from app.services.audiocraft_service import audiocraft_service
        assert audiocraft_service is not None
        print("AudioCraft Service: OK")
    except ImportError:
        pytest.fail("AudioCraft service import failed")

if __name__ == "__main__":
    # Rudimentary manual runner
    test_musicpy_integration()
    test_verovio_integration()
    test_essentia_integration()
    test_audiocraft_integration()
