from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class AlignmentSource(str, Enum):
    AUTOMATIC = "automatic"
    REFINED = "refined"
    MANUAL = "manual"


class SectionType(str, Enum):
    INTRO = "intro"
    VERSE = "verse"
    PRE_CHORUS = "pre_chorus"
    CHORUS = "chorus"
    BRIDGE = "bridge"
    OUTRO = "outro"
    INSTRUMENTAL = "instrumental"
    OTHER = "other"


class WordTiming(BaseModel):
    id: str = Field(default_factory=lambda: f"w-{uuid.uuid4().hex[:8]}")
    display_text: str
    alignment_text: str
    start_ms: int
    end_ms: int
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: AlignmentSource = AlignmentSource.AUTOMATIC
    manually_verified: bool = False


class LineTiming(BaseModel):
    id: str = Field(default_factory=lambda: f"l-{uuid.uuid4().hex[:8]}")
    section_id: Optional[str] = None
    display_text: str
    alignment_text: str
    start_ms: int
    end_ms: int
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: AlignmentSource = AlignmentSource.AUTOMATIC
    manually_verified: bool = False
    words: List[WordTiming] = Field(default_factory=list)


class SectionTiming(BaseModel):
    id: str = Field(default_factory=lambda: f"s-{uuid.uuid4().hex[:8]}")
    type: SectionType = SectionType.VERSE
    display_label: str = "Verse"
    start_ms: int
    end_ms: int


class AudioMetadata(BaseModel):
    original_file: str
    working_file: Optional[str] = None
    duration_ms: int
    codec: Optional[str] = None
    bitrate_kbps: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    artwork_path: Optional[str] = None


class ValidationDiagnostic(BaseModel):
    severity: str  # "info", "warning", "error"
    code: str
    message: str
    line_id: Optional[str] = None
    start_ms: Optional[int] = None
    end_ms: Optional[int] = None


class CanonicalTimeline(BaseModel):
    schema_version: str = "1.0"
    project_id: str
    title: str = "Untitled"
    artist: str = "Unknown Artist"
    language: str = "en"
    audio: AudioMetadata
    sections: List[SectionTiming] = Field(default_factory=list)
    lines: List[LineTiming] = Field(default_factory=list)
    diagnostics: List[ValidationDiagnostic] = Field(default_factory=list)
    overall_confidence: float = 1.0


class ProjectCreateRequest(BaseModel):
    title: Optional[str] = None
    artist: Optional[str] = None
    language: str = "en"


class ProjectResponse(BaseModel):
    project_id: str
    title: str
    artist: str
    language: str
    status: str
    created_at: str
    has_audio: bool = False
    has_lyrics: bool = False
    canonical_timeline: Optional[CanonicalTimeline] = None
