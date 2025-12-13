from typing import Optional
from pathlib import Path
import logging

try:
    import verovio
    VEROVIO_AVAILABLE = True
except ImportError:
    VEROVIO_AVAILABLE = False
    print("Verovio not found. Notation rendering disabled.")

logger = logging.getLogger(__name__)

class VerovioService:
    """
    Service for rendering MusicXML/MEI/MIDI to SVG using Verovio.
    """
    
    def __init__(self):
        if VEROVIO_AVAILABLE:
            self.tk = verovio.toolkit()
    
    def render_midi_to_svg(self, midi_path: Path) -> str:
        """
        Render a MIDI file to SVG string.
        Verovio can load MIDI directly and render it.
        """
        if not VEROVIO_AVAILABLE:
            return "<svg><text>Verovio not installed</text></svg>"
            
        try:
            # Load MIDI data
            self.tk.loadFile(str(midi_path))
            
            # Set options for clearer rendering
            self.tk.setOptions({
                "pageWidth": 2100, # A4ish
                "pageHeight": 2970,
                "scale": 40,
                "adjustPageHeight": True,
                "breaks": "auto"
            })
            
            # Render first page
            svg_data = self.tk.renderToSVG(1)
            return svg_data
            
        except Exception as e:
            logger.error(f"Verovio rendering failed: {e}")
            return f"<svg><text>Error: {str(e)}</text></svg>"

verovio_service = VerovioService()
