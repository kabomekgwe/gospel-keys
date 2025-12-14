"""Transcription service - orchestrates the processing pipeline"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional
import uuid
import shutil
from fastapi import UploadFile

from app.core.config import settings
from app.schemas.transcription import (
    TranscriptionJob,
    TranscriptionOptions,
    TranscriptionResult,
    JobStatus,
)
from app.pipeline.downloader import download_video
from app.pipeline.audio_extractor import extract_audio, get_audio_info
from app.pipeline.source_separator import isolate_piano
from app.pipeline.midi_converter import transcribe_audio, estimate_key
from app.pipeline.chord_detector import detect_chords


class TranscriptionService:
    """Service for managing transcription jobs and pipeline execution"""
    
    def __init__(self):
        self.jobs: dict[str, TranscriptionJob] = {}
        settings.ensure_directories()
    
    async def process_url(self, url: str, options: TranscriptionOptions) -> str:
        """
        Create job and start URL-based transcription pipeline
        
        Args:
            url: YouTube video URL
            options: Processing options
        
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        # Create job
        job = TranscriptionJob(
            id=job_id,
            status=JobStatus.QUEUED,
            progress=0,
            source_url=url,
            options=options,
        )
        
        self.jobs[job_id] = job
        
        # Start pipeline in background
        asyncio.create_task(self._execute_url_pipeline(job_id))
        
        return job_id
    
    async def process_file(self, file: UploadFile, options: TranscriptionOptions) -> str:
        """
        Create job and start file-based transcription pipeline
        
        Args:
            file: Uploaded audio/video file
            options: Processing options
        
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        
        # Save uploaded file
        upload_path = settings.upload_dir / f"{job_id}_{file.filename}"
        
        async with asyncio.Lock():
            with open(upload_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        
        # Create job
        job = TranscriptionJob(
            id=job_id,
            status=JobStatus.QUEUED,
            progress=0,
            source_file=file.filename,
            options=options,
        )
        
        self.jobs[job_id] = job
        
        # Start pipeline in background
        asyncio.create_task(self._execute_file_pipeline(job_id, upload_path))
        
        return job_id
    
    async def _execute_url_pipeline(self, job_id: str):
        """Execute full URL pipeline with error handling"""
        try:
            job = self.jobs[job_id]
            job.status = JobStatus.DOWNLOADING
            job.current_step = "Downloading video..."
            job.started_at = datetime.now()
            job.progress = 5
            
            # Download video
            download_dir = settings.upload_dir / job_id
            downloaded_file, title = await download_video(job.source_url, download_dir)
            
            # Execute common pipeline
            await self._execute_common_pipeline(job_id, downloaded_file, title)
            
        except Exception as e:
            await self._handle_error(job_id, str(e))
    
    async def _execute_file_pipeline(self, job_id: str, file_path: Path):
        """Execute full file pipeline with error handling"""
        try:
            job = self.jobs[job_id]
            job.status = JobStatus.PROCESSING
            job.current_step = "Processing uploaded file..."
            job.started_at = datetime.now()
            job.progress = 10
            
            # Execute common pipeline
            await self._execute_common_pipeline(job_id, file_path, job.source_file)
            
        except Exception as e:
            await self._handle_error(job_id, str(e))
    
    async def _execute_common_pipeline(
        self,
        job_id: str,
        input_file: Path,
        source_title: Optional[str] = None
    ):
        """Execute common processing steps for both URL and file inputs"""
        try:
            job = self.jobs[job_id]
            output_dir = settings.output_dir / job_id
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Step 1: Extract audio info
            job.status = JobStatus.PROCESSING
            job.current_step = "Extracting audio..."
            job.progress = 15
            
            audio_info = await get_audio_info(input_file)
            duration = audio_info['duration']
            
            # Step 2: Extract/convert audio
            audio_path = output_dir / "audio.wav"
            await extract_audio(input_file, audio_path)
            job.progress = 25
            
            # Step 3: Isolate piano (optional)
            piano_audio_path = audio_path
            if job.options.isolate_piano:
                job.current_step = "Isolating piano..."
                job.progress = 30
                piano_audio_path = await isolate_piano(audio_path, output_dir)
                job.progress = 50
            
            # Step 4: Transcribe to MIDI
            job.current_step = "Transcribing to MIDI..."
            job.progress = 55
            
            midi_path = output_dir / "transcription.mid"
            notes, midi_file, estimated_tempo = await transcribe_audio(
                piano_audio_path,
                midi_path
            )
            job.progress = 75
            
            # Step 5: Detect chords (optional)
            chords = []
            if job.options.detect_chords:
                job.status = JobStatus.ANALYZING
                job.current_step = "Detecting chords..."
                job.progress = 70

                chords = await detect_chords(piano_audio_path)
                job.progress = 75

            # Step 6: Advanced Music Theory Analysis (music21)
            job.current_step = "Analyzing music theory..."
            job.progress = 80

            from app.services.music_theory import music_theory_service
            analysis_result = music_theory_service.analyze_score(midi_path)

            # Use analyzed key if available, otherwise fall back to estimation
            # Using the analyzed key is much more accurate than simple estimation
            estimated_key = analysis_result.get("key") or estimate_key(notes)

            # Step 7: NEW - Voicing Analysis
            job.current_step = "Analyzing voicings..."
            job.progress = 85

            from app.pipeline.voicing_analyzer import analyze_all_voicings
            from app.gospel import Note
            from app.schemas.transcription import VoicingInfo

            # Convert NoteEvent to Note for voicing analyzer
            note_objects = [Note(pitch=n.pitch, start_time=n.start_time, end_time=n.end_time, velocity=n.velocity, hand=None) for n in notes]

            # Analyze voicings for all chords
            voicings = await analyze_all_voicings(note_objects, chords)

            # Attach voicing info to corresponding chords
            for i, chord in enumerate(chords):
                if i < len(voicings):
                    voicing = voicings[i]
                    chord.voicing = VoicingInfo(
                        voicing_type=voicing.voicing_type.value,
                        notes=voicing.notes,
                        note_names=voicing.note_names,
                        intervals=voicing.intervals,
                        width_semitones=voicing.width_semitones,
                        inversion=voicing.inversion,
                        has_root=voicing.has_root,
                        has_third=voicing.has_third,
                        has_seventh=voicing.has_seventh,
                        extensions=voicing.extensions,
                        complexity_score=voicing.complexity_score,
                        hand_span_inches=voicing.hand_span_inches
                    )
                # Add start_time and end_time for compatibility
                chord.start_time = chord.time
                chord.end_time = chord.time + chord.duration

            # Step 8: NEW - Progression Detection
            job.current_step = "Detecting progressions..."
            job.progress = 90

            from app.pipeline.progression_detector import detect_progressions_async
            from app.schemas.transcription import ProgressionPattern

            progression_matches = await detect_progressions_async(chords, estimated_key)
            patterns = [
                ProgressionPattern(
                    pattern_name=match.pattern_name,
                    genre=match.genre.value,
                    roman_numerals=match.roman_numerals,
                    start_index=match.start_index,
                    end_index=match.end_index,
                    key=match.key,
                    confidence=match.confidence,
                    description=match.description
                )
                for match in progression_matches
            ]

            # Step 9: NEW - Reharmonization Suggestions
            job.current_step = "Generating reharmonization ideas..."
            job.progress = 95

            from app.pipeline.reharmonization_engine import suggest_reharmonizations_async
            from app.schemas.transcription import ReharmonizationSuggestion

            # Generate reharmonization suggestions for each chord
            for chord in chords:
                chord_dict = {
                    'root': chord.root,
                    'quality': chord.quality
                }
                suggestions = await suggest_reharmonizations_async(chord_dict, estimated_key)
                chord.reharmonizations = [
                    ReharmonizationSuggestion(
                        original_chord=sugg.original_chord,
                        suggested_chord=sugg.suggested_chord,
                        reharmonization_type=sugg.reharmonization_type.value,
                        explanation=sugg.explanation,
                        jazz_level=sugg.jazz_level,
                        voice_leading_quality=sugg.voice_leading_quality
                    )
                    for sugg in suggestions
                ]

            # Calculate average voicing complexity
            voicing_complexity_avg = None
            if voicings:
                voicing_complexity_avg = sum(v.complexity_score for v in voicings) / len(voicings)

            # Generate progression summary
            progression_summary = None
            if patterns:
                pattern_names = [p.pattern_name for p in patterns[:3]]  # Top 3
                progression_summary = f"Detected {len(patterns)} patterns: {', '.join(pattern_names)}"

            # Create result
            midi_url = f"/files/{job_id}/transcription.mid"

            result = TranscriptionResult(
                song_id=job_id,
                notes=notes,
                chords=chords,
                patterns=patterns,
                tempo=estimated_tempo if job.options.detect_tempo else None,
                key=estimated_key,
                duration=duration,
                midi_url=midi_url,
                source_title=source_title,
                voicing_complexity_avg=voicing_complexity_avg,
                progression_summary=progression_summary,
                # We could extend TranscriptionResult to include time_signature, etc.
                # For now, we'll store it in the database via the song record
            )
            
            # Mark job as complete
            job.status = JobStatus.COMPLETE
            job.current_step = "Complete"
            job.progress = 100
            job.result = result
            job.completed_at = datetime.now()
            
            # Save to database
            await self._save_to_database(job_id, result, source_title, analysis_result)
            
        except Exception as e:
            await self._handle_error(job_id, str(e))
    
    async def _save_to_database(
        self,
        job_id: str,
        result: TranscriptionResult,
        source_title: Optional[str] = None,
        analysis_result: Optional[dict] = None
    ):
        """Save transcription result to SQLite database"""
        try:
            from app.database.session import async_session_maker
            from app.database.models import Song, SongNote, SongChord
            
            async with async_session_maker() as db:
                # Create song record
                song = Song(
                    id=job_id,
                    title=source_title or "Untitled",
                    duration=result.duration,
                    tempo=result.tempo,
                    key_signature=result.key,
                    time_signature=analysis_result.get("time_signature", "4/4") if analysis_result else "4/4",
                    midi_file_path=str(settings.output_dir / job_id / "transcription.mid"),
                    created_at=datetime.now(),
                    last_accessed_at=datetime.now(),
                )
                
                # Get job to add source info
                job = self.jobs.get(job_id)
                if job:
                    song.source_url = job.source_url
                    song.source_file = job.source_file
                
                db.add(song)
                
                # Add notes
                for note_data in result.notes:
                    note = SongNote(
                        song_id=job_id,
                        pitch=note_data.pitch,
                        start_time=note_data.start_time,
                        end_time=note_data.end_time,
                        velocity=note_data.velocity,
                    )
                    db.add(note)
                
                # Add chords
                for chord_data in result.chords:
                    chord = SongChord(
                        song_id=job_id,
                        time=chord_data.time,
                        duration=chord_data.duration,
                        chord=chord_data.chord,
                        confidence=chord_data.confidence,
                        root=chord_data.root,
                        quality=chord_data.quality,
                    )
                    db.add(chord)
                
                await db.commit()
        except Exception as e:
            # Log error but don't fail the job
            print(f"Warning: Failed to save to database: {e}")
    
    async def _handle_error(self, job_id: str, error_message: str):
        """Handle pipeline errors"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job.status = JobStatus.FAILED
            job.error_message = error_message
            job.current_step = "Failed"
            job.completed_at = datetime.now()
    
    def get_job(self, job_id: str) -> Optional[TranscriptionJob]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def list_jobs(
        self,
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> list[TranscriptionJob]:
        """List jobs with optional filtering"""
        jobs_list = list(self.jobs.values())
        
        # Filter by status
        if status:
            jobs_list = [j for j in jobs_list if j.status.value == status]
        
        # Sort by creation time (newest first)
        jobs_list.sort(key=lambda j: j.created_at, reverse=True)
        
        # Apply pagination
        return jobs_list[offset:offset + limit]
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        
        # Only cancel if job is still in progress
        if job.status in [JobStatus.QUEUED, JobStatus.DOWNLOADING, JobStatus.PROCESSING, JobStatus.ANALYZING]:
            job.status = JobStatus.CANCELLED
            job.current_step = "Cancelled"
            job.completed_at = datetime.now()
        
        return True
    
    def delete_job(self, job_id: str) -> bool:
        """Delete job and associated files"""
        if job_id not in self.jobs:
            return False
        
        # Delete associated files
        output_dir = settings.output_dir / job_id
        if output_dir.exists():
            shutil.rmtree(output_dir)
        
        upload_dir = settings.upload_dir / job_id
        if upload_dir.exists():
            shutil.rmtree(upload_dir)
        
        # Also check for direct upload files
        for upload_file in settings.upload_dir.glob(f"{job_id}_*"):
            upload_file.unlink()
        
        # Remove from jobs dict
        del self.jobs[job_id]
        
        return True
