"""
Base Generator for all genre-specific music generation services.

This module provides a comprehensive base class that eliminates code duplication
across Gospel, Jazz, Blues, Neo-soul, and Classical generators.

Architecture:
- Template Method Pattern: Defines the generation pipeline with hooks for customization
- Strategy Pattern: Allows genre-specific arrangers to be injected
- DRY Principle: All common logic centralized here

Usage:
    class GospelGeneratorService(BaseGenreGenerator):
        def __init__(self):
            super().__init__(
                genre_name="Gospel",
                arranger_class=GospelArranger,
                request_schema=GenerateGospelRequest,
                response_schema=GenerateGospelResponse,
                status_schema=GospelGeneratorStatus,
                default_tempo=72,
                output_subdir="gospel_generated"
            )
"""

import base64
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Type, Optional, List, Tuple, Dict, Any
import google.generativeai as genai

from app.core.config import settings
from app.services.generator_utils import (
    parse_json_from_response,
    export_to_midi,
    get_notes_preview,
    parse_description_fallback
)


# Configure Gemini globally
if settings.google_api_key:
    genai.configure(api_key=settings.google_api_key)


class BaseGenreGenerator(ABC):
    """
    Abstract base class for all genre-specific music generators.

    This class implements the Template Method pattern, defining the standard
    generation pipeline while allowing subclasses to customize specific steps.

    Attributes:
        genre_name: Human-readable genre name (e.g., "Gospel", "Jazz")
        gemini_model: Gemini AI model instance (None if unavailable)
        arranger: Genre-specific arranger instance
        default_tempo: Default BPM for this genre
        output_subdir: Output directory for MIDI files
    """

    def __init__(
        self,
        genre_name: str,
        arranger_class: Type,
        request_schema: Type,
        response_schema: Type,
        status_schema: Type,
        default_tempo: int = 120,
        output_subdir: str = "generated"
    ):
        """
        Initialize base generator with genre-specific configuration.

        Args:
            genre_name: Display name for this genre
            arranger_class: Class to instantiate for arrangements
            request_schema: Pydantic schema for requests
            response_schema: Pydantic schema for responses
            status_schema: Pydantic schema for status
            default_tempo: Default BPM if not specified
            output_subdir: Subdirectory under outputs/ for MIDI files
        """
        self.genre_name = genre_name
        self.request_schema = request_schema
        self.response_schema = response_schema
        self.status_schema = status_schema
        self.default_tempo = default_tempo
        self.output_subdir = output_subdir

        # Initialize Gemini model
        self.gemini_model = self._init_gemini()

        # Initialize genre-specific arranger
        self.arranger = self._init_arranger(arranger_class)

    def _init_gemini(self) -> Optional[Any]:
        """
        Initialize Gemini AI model.

        Returns:
            GenerativeModel instance or None if unavailable
        """
        if settings.google_api_key:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                print(f"✅ Gemini API initialized for {self.genre_name}")
                return model
            except Exception as e:
                print(f"⚠️  Gemini initialization failed for {self.genre_name}: {e}")
        return None

    def _init_arranger(self, arranger_class: Type) -> Any:
        """
        Initialize genre-specific arranger.

        Args:
            arranger_class: Arranger class to instantiate

        Returns:
            Arranger instance

        Raises:
            Exception: If arranger initialization fails
        """
        try:
            arranger = arranger_class()
            print(f"✅ {self.genre_name} arranger initialized")
            return arranger
        except Exception as e:
            print(f"❌ {self.genre_name} arranger failed: {e}")
            raise

    # =====================================================================
    # ABSTRACT METHODS - Must be implemented by subclasses
    # =====================================================================

    @abstractmethod
    def _get_style_context(self, complexity: int = 5, style: str = "") -> str:
        """
        Get genre-specific style context for AI prompts.

        Args:
            complexity: Harmony complexity (1-10)
            style: Specific style nuance

        Returns:
            String describing genre conventions, harmony, and style
        """
        pass

    @abstractmethod
    def _get_default_progression(self, key: str) -> List[str]:
        """
        Get fallback chord progression for this genre.

        Args:
            key: Musical key (e.g., "C", "Am")

        Returns:
            List of chord symbols
        """
        pass

    @abstractmethod
    def get_status(self):
        """
        Get current status of this generator.

        Returns:
            Status schema instance (genre-specific)
        """
        pass

    # =====================================================================
    # TEMPLATE METHOD - Standard generation pipeline
    # =====================================================================

    async def generate_arrangement(self, request) -> Any:
        """
        Main generation pipeline (Template Method).

        Standard workflow:
        1. Generate chord progression (Gemini or fallback)
        2. Arrange with genre-specific rules
        3. Export to MIDI
        4. Build response

        Args:
            request: Request schema instance (genre-specific)

        Returns:
            Response schema instance (genre-specific)
        """
        try:
            # Step 1: Generate chord progression
            if self.gemini_model and request.include_progression:
                print(f"🎵 Generating {self.genre_name} chord progression with Gemini...")
                chords, key, tempo, analysis = await self._generate_progression_with_gemini(
                    request.description,
                    request.key,
                    request.tempo,
                    request.num_bars,
                    getattr(request, 'complexity', 5),
                    getattr(request, 'style', '')
                )
            else:
                print(f"📝 Using fallback progression for {self.genre_name}...")
                chords, key, tempo = self._parse_description_with_fallback(
                    request.description,
                    request.key,
                    request.tempo
                )
                analysis = []

            # Step 2: Generate MIDI arrangement
            print(f"🎹 Generating {self.genre_name} arrangement...")
            arrangement = self._create_arrangement(
                chords=chords,
                key=key,
                tempo=tempo,
                request=request
            )

            # Step 3: Export to MIDI
            print(f"💾 Exporting {self.genre_name} MIDI...")
            midi_path, midi_base64 = export_to_midi(
                arrangement,
                self.output_subdir,
                self.genre_name.lower()
            )

            # Step 4: Build response
            return self._build_success_response(
                midi_path=midi_path,
                midi_base64=midi_base64,
                arrangement=arrangement,
                analysis=analysis,
                request=request
            )

        except Exception as e:
            print(f"❌ {self.genre_name} generation failed: {e}")
            import traceback
            traceback.print_exc()
            return self._build_error_response(str(e))

    # =====================================================================
    # PROGRESSION GENERATION - Gemini-powered or fallback
    # =====================================================================

    async def _generate_progression_with_gemini(
        self,
        description: str,
        key: Optional[str],
        tempo: Optional[int],
        num_bars: int,
        complexity: int = 5,
        style: str = ""
    ) -> Tuple[List[str], str, int, List]:
        """
        Generate chord progression using Gemini AI.

        Args:
            description: Natural language description
            key: Explicit key override (optional)
            tempo: Explicit tempo override (optional)
            num_bars: Number of bars to generate
            complexity: Complexity level (1-10)
            style: Specific style nuance

        Returns:
            Tuple of (chords, key, tempo, analysis)
        """
        # Build genre-specific prompt
        style_context = self._get_style_context(complexity, style)

        prompt = f"""You are an expert {self.genre_name} pianist and music theorist.

Generate a {num_bars}-bar {self.genre_name} piano chord progression.
Description: "{description}"
Style: {style if style else "Standard " + self.genre_name}
Complexity: {complexity}/10

{"Key: " + key if key else "Choose an appropriate key"}
{"Tempo: " + str(tempo) + " BPM" if tempo else "Choose an appropriate tempo"}

{style_context}

Return ONLY valid JSON with this exact structure:
{{
  "key": "C",
  "tempo": {self.default_tempo},
  "chords": [
    {{
      "symbol": "Cmaj9",
      "function": "I",
      "notes": ["C", "E", "G", "B", "D"],
      "comment": "Tonic with added 9th"
    }}
  ]
}}

Generate {num_bars} chords total. Each chord should have symbol, function, notes, and comment."""

        # Call Gemini
        response = self.gemini_model.generate_content(prompt)

        # Parse JSON response using shared utility
        data = parse_json_from_response(response.text.strip())

        # Extract data
        generated_key = data.get("key", key or "C")
        generated_tempo = data.get("tempo", tempo or self.default_tempo)
        chord_data = data.get("chords", [])

        # Build chord list and analysis
        chords = [c["symbol"] for c in chord_data]
        analysis = self._build_chord_analysis(chord_data)

        return chords, generated_key, generated_tempo, analysis

    def _parse_description_with_fallback(
        self,
        description: str,
        key: Optional[str],
        tempo: Optional[int]
    ) -> Tuple[List[str], str, int]:
        """
        Parse description without Gemini (fallback mode).

        Args:
            description: User's natural language description
            key: Explicit key override (optional)
            tempo: Explicit tempo override (optional)

        Returns:
            Tuple of (chords, key, tempo)
        """
        # Get genre-specific default progression
        default_chords = self._get_default_progression(key or "C")

        # Use shared utility for parsing
        chords, parsed_key, parsed_tempo = parse_description_fallback(
            description,
            key,
            tempo,
            default_chords,
            self.default_tempo
        )

        return chords, parsed_key, parsed_tempo

    def _build_chord_analysis(self, chord_data: List[Dict]) -> List:
        """
        Build ChordAnalysis objects from raw chord data.

        This method can be overridden by subclasses if they need different
        analysis schema structures.

        Args:
            chord_data: List of chord dictionaries from Gemini

        Returns:
            List of ChordAnalysis objects (schema-specific)
        """
        # Import dynamically to avoid circular dependencies
        # Subclasses can override this method to use their own schema
        try:
            from app.schemas.gospel import ChordAnalysis

            return [
                ChordAnalysis(
                    symbol=c["symbol"],
                    function=c.get("function", ""),
                    notes=c.get("notes", []),
                    comment=c.get("comment")
                )
                for c in chord_data
            ]
        except ImportError:
            # If ChordAnalysis not available, return raw dicts
            return chord_data

    # =====================================================================
    # ARRANGEMENT CREATION - Calls genre-specific arranger
    # =====================================================================

    def _create_arrangement(
        self,
        chords: List[str],
        key: str,
        tempo: int,
        request: Any
    ) -> Any:
        """
        Create MIDI arrangement using genre-specific arranger.

        Args:
            chords: List of chord symbols
            key: Musical key
            tempo: BPM
            request: Original request (for additional parameters)

        Returns:
            Arrangement object
        """
        # Standard arrangement parameters
        arrange_params = {
            "chords": chords,
            "key": key,
            "bpm": tempo,
            "time_signature": (4, 4)  # Default to 4/4
        }

        # Add optional parameters if present in request
        if hasattr(request, 'application'):
            arrange_params['application'] = request.application.value

        if hasattr(request, 'complexity'):
            arrange_params['complexity'] = request.complexity

        if hasattr(request, 'ai_percentage'):
            # For hybrid arrangers that support AI blending
            if hasattr(self.arranger, 'set_ai_percentage'):
                self.arranger.set_ai_percentage(request.ai_percentage)

        return self.arranger.arrange_progression(**arrange_params)

    # =====================================================================
    # RESPONSE BUILDING - Constructs success/error responses
    # =====================================================================

    def _build_success_response(
        self,
        midi_path: Path,
        midi_base64: str,
        arrangement: Any,
        analysis: List,
        request: Any
    ) -> Any:
        """
        Build successful generation response.

        Args:
            midi_path: Path to generated MIDI file
            midi_base64: Base64-encoded MIDI data
            arrangement: Arrangement object
            analysis: Chord analysis (if available)
            request: Original request

        Returns:
            Response schema instance (genre-specific)
        """
        return self.response_schema(
            success=True,
            midi_file_path=str(midi_path),
            midi_base64=midi_base64,
            progression=analysis if (analysis and request.include_progression) else None,
            arrangement_info={
                "tempo": arrangement.tempo,
                "key": arrangement.key,
                "time_signature": f"{arrangement.time_signature[0]}/{arrangement.time_signature[1]}",
                "total_bars": arrangement.total_bars,
                "total_notes": len(arrangement.left_hand_notes) + len(arrangement.right_hand_notes),
                "left_hand_notes": len(arrangement.left_hand_notes),
                "right_hand_notes": len(arrangement.right_hand_notes),
                "duration_seconds": round(arrangement.total_duration_seconds, 2),
                "application": getattr(arrangement, 'application', 'standard'),
            },
            notes_preview=get_notes_preview(arrangement),
            generation_method=self._determine_generation_method(request)
        )

    def _build_error_response(self, error_message: str) -> Any:
        """
        Build error response.

        Args:
            error_message: Error description

        Returns:
            Response schema instance with error
        """
        return self.response_schema(
            success=False,
            generation_method="failed",
            error=error_message
        )

    def _determine_generation_method(self, request: Any) -> str:
        """
        Determine generation method string for response.

        Args:
            request: Original request

        Returns:
            Method description (e.g., "gemini+rules", "rules-only")
        """
        if self.gemini_model and request.include_progression:
            if hasattr(request, 'ai_percentage') and request.ai_percentage > 0:
                return "gemini+ai+rules"
            return "gemini+rules"
        elif hasattr(request, 'ai_percentage') and request.ai_percentage > 0:
            return "ai+rules"
        else:
            return "rules-only"

    # =====================================================================
    # OPTIONAL HOOKS - Can be overridden for advanced features
    # =====================================================================

    def _get_knowledge_base_context(self) -> str:
        """
        Get additional context from knowledge base (if available).

        Override this method to integrate with music knowledge bases,
        style guides, or reference materials.

        Returns:
            Additional context string for prompts
        """
        return ""
