"""
Pydantic models for request/response validation
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, HttpUrl, validator


class AudioFormat(str, Enum):
    """Supported audio formats"""
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"
    M4A = "m4a"


class ProcessingStatus(str, Enum):
    """Status of audio processing jobs"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingIntent(str, Enum):
    """AI-detected intent for audio processing"""
    DENOISE = "denoise"
    TRANSCRIBE = "transcribe"
    TRIM = "trim"
    SEPARATE = "separate"
    ANALYZE_SENTIMENT = "analyze_sentiment"
    TEXT_TO_SPEECH = "text_to_speech"
    CUSTOM_WORKFLOW = "custom_workflow"


class AudioProcessingRequest(BaseModel):
    """Base request model for audio processing"""
    audio_url: Optional[HttpUrl] = Field(None, description="URL to audio file")
    audio_data: Optional[bytes] = Field(None, description="Raw audio data")
    format: AudioFormat = Field(AudioFormat.WAV, description="Audio format")
    callback_url: Optional[HttpUrl] = Field(None, description="Webhook URL for async notifications")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('audio_url', 'audio_data')
    def check_audio_provided(cls, v, values):
        """Ensure either audio_url or audio_data is provided"""
        if 'audio_url' in values and values['audio_url'] is None and v is None:
            if 'audio_data' not in values or values['audio_data'] is None:
                raise ValueError("Either audio_url or audio_data must be provided")
        return v
    
    class Config:
        use_enum_values = True


class DenoiseRequest(AudioProcessingRequest):
    """Request for audio denoising"""
    noise_reduction_level: float = Field(0.8, ge=0.0, le=1.0, description="Noise reduction strength")
    enhance_speech: bool = Field(True, description="Enhance speech frequencies")


class TranscriptionRequest(AudioProcessingRequest):
    """Request for speech-to-text transcription"""
    language: Optional[str] = Field(None, description="ISO language code (auto-detect if None)")
    enable_diarization: bool = Field(False, description="Enable speaker diarization")
    timestamps: bool = Field(True, description="Include word-level timestamps")
    model: str = Field("base", description="Whisper model size: tiny, base, small, medium, large")


class TrimRequest(AudioProcessingRequest):
    """Request for smart trimming"""
    silence_threshold_db: float = Field(-40.0, description="Silence threshold in dB")
    min_silence_duration: float = Field(0.5, description="Minimum silence duration in seconds")
    remove_silence: bool = Field(True, description="Remove silence segments")


class SeparationRequest(AudioProcessingRequest):
    """Request for source separation"""
    separation_type: str = Field("vocals", description="Type: vocals, drums, bass, other")
    model: str = Field("htdemucs", description="Separation model")


class SentimentRequest(AudioProcessingRequest):
    """Request for sentiment analysis"""
    include_emotions: bool = Field(True, description="Include emotion detection")
    confidence_threshold: float = Field(0.5, ge=0.0, le=1.0)


class TTSRequest(BaseModel):
    """Request for text-to-speech"""
    text: str = Field(..., description="Text to convert to speech")
    voice_id: Optional[str] = Field(None, description="Voice ID for cloning")
    language: str = Field("en", description="Language code")
    speed: float = Field(1.0, ge=0.5, le=2.0, description="Speech speed multiplier")
    format: AudioFormat = Field(AudioFormat.MP3, description="Output audio format")


class AudioProcessingResponse(BaseModel):
    """Base response model for audio processing"""
    task_id: str = Field(..., description="Unique task identifier")
    status: ProcessingStatus = Field(..., description="Current processing status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    output_url: Optional[HttpUrl] = Field(None, description="URL to processed audio")
    output_data: Optional[bytes] = Field(None, description="Raw processed audio data")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    
    class Config:
        use_enum_values = True


class TranscriptionResponse(AudioProcessingResponse):
    """Response for transcription requests"""
    transcript: Optional[str] = None
    segments: Optional[List[Dict[str, Any]]] = None
    speakers: Optional[List[str]] = None
    language: Optional[str] = None
    confidence: Optional[float] = None


class SentimentResponse(AudioProcessingResponse):
    """Response for sentiment analysis"""
    sentiment: Optional[str] = None  # positive, negative, neutral
    sentiment_score: Optional[float] = None
    emotions: Optional[Dict[str, float]] = None
    transcript: Optional[str] = None


class SeparationResponse(AudioProcessingResponse):
    """Response for source separation"""
    separated_tracks: Optional[Dict[str, HttpUrl]] = Field(
        None, 
        description="Dictionary of track names to URLs"
    )


class WorkflowResponse(AudioProcessingResponse):
    """Response for orchestrated workflows"""
    intent: Optional[ProcessingIntent] = None
    steps_completed: List[str] = Field(default_factory=list)
    intermediate_results: Dict[str, Any] = Field(default_factory=dict)
