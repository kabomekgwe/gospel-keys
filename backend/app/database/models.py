"""SQLAlchemy database models for Gospel Keys

Defines all database tables using SQLAlchemy 2.0 declarative style with async support.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import String, Float, Integer, Boolean, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for all database models"""
    pass


class Song(Base):
    """Main song/transcription entity"""
    __tablename__ = "songs"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    artist: Mapped[Optional[str]] = mapped_column(String)
    source_url: Mapped[Optional[str]] = mapped_column(String)
    source_file: Mapped[Optional[str]] = mapped_column(String)
    duration: Mapped[Optional[float]] = mapped_column(Float)
    tempo: Mapped[Optional[float]] = mapped_column(Float)
    key_signature: Mapped[Optional[str]] = mapped_column(String)
    time_signature: Mapped[Optional[str]] = mapped_column(String)
    difficulty: Mapped[Optional[str]] = mapped_column(String)
    midi_file_path: Mapped[Optional[str]] = mapped_column(String)
    audio_file_path: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    notes: Mapped[List["SongNote"]] = relationship(
        back_populates="song",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    chords: Mapped[List["SongChord"]] = relationship(
        back_populates="song",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    annotations: Mapped[List["Annotation"]] = relationship(
        back_populates="song",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    snippets: Mapped[List["Snippet"]] = relationship(
        back_populates="song",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    tags: Mapped[List["SongTag"]] = relationship(
        back_populates="song",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class SongNote(Base):
    """Individual MIDI note within a song"""
    __tablename__ = "song_notes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    song_id: Mapped[str] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"))
    pitch: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    velocity: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Relationship
    song: Mapped["Song"] = relationship(back_populates="notes")


class SongChord(Base):
    """Detected chord within a song"""
    __tablename__ = "song_chords"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    song_id: Mapped[str] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"))
    time: Mapped[float] = mapped_column(Float, nullable=False)
    duration: Mapped[float] = mapped_column(Float, nullable=False)
    chord: Mapped[str] = mapped_column(String, nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    root: Mapped[str] = mapped_column(String, nullable=False)
    quality: Mapped[str] = mapped_column(String, nullable=False)
    bass_note: Mapped[Optional[str]] = mapped_column(String)
    
    # Relationship
    song: Mapped["Song"] = relationship(back_populates="chords")


class Tag(Base):
    """Tag for organizing songs"""
    __tablename__ = "tags"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    
    # Relationship
    songs: Mapped[List["SongTag"]] = relationship(back_populates="tag", cascade="all, delete-orphan")


class SongTag(Base):
    """Many-to-many relationship between songs and tags"""
    __tablename__ = "song_tags"
    
    song_id: Mapped[str] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
    
    # Relationships
    song: Mapped["Song"] = relationship(back_populates="tags")
    tag: Mapped["Tag"] = relationship(back_populates="songs")


class Annotation(Base):
    """User annotation on a song at a specific timestamp"""
    __tablename__ = "annotations"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    song_id: Mapped[str] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"))
    time: Mapped[float] = mapped_column(Float, nullable=False)
    note_text: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)  # practice_note, theory_insight, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Relationship
    song: Mapped["Song"] = relationship(back_populates="annotations")


class Snippet(Base):
    """Extracted practice snippet from a song"""
    __tablename__ = "snippets"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    song_id: Mapped[str] = mapped_column(ForeignKey("songs.id", ondelete="CASCADE"))
    label: Mapped[str] = mapped_column(String, nullable=False)
    start_time: Mapped[float] = mapped_column(Float, nullable=False)
    end_time: Mapped[float] = mapped_column(Float, nullable=False)
    difficulty: Mapped[Optional[str]] = mapped_column(String)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    practice_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Relationship
    song: Mapped["Song"] = relationship(back_populates="snippets")
    practice_sessions: Mapped[List["PracticeSession"]] = relationship(
        back_populates="snippet",
        cascade="all, delete-orphan"
    )


class PracticeSession(Base):
    """Record of a practice session"""
    __tablename__ = "practice_sessions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    song_id: Mapped[Optional[str]] = mapped_column(ForeignKey("songs.id", ondelete="SET NULL"))
    snippet_id: Mapped[Optional[str]] = mapped_column(ForeignKey("snippets.id", ondelete="SET NULL"))
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    tempo_multiplier: Mapped[float] = mapped_column(Float, default=1.0)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    
    # Relationships
    snippet: Mapped[Optional["Snippet"]] = relationship(back_populates="practice_sessions")
