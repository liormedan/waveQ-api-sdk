"""
Main WaveQ SDK Client for interacting with the AI Audio Agent API
"""

import asyncio
import httpx
from pathlib import Path
from typing import Optional, Union, BinaryIO
from urllib.parse import urljoin

from waveq.models import (
    AudioProcessingResponse,
    DenoiseRequest,
    TranscriptionRequest,
    TranscriptionResponse,
    TrimRequest,
    SeparationRequest,
    SeparationResponse,
    SentimentRequest,
    SentimentResponse,
    TTSRequest,
    ProcessingStatus,
)
from waveq.exceptions import (
    AuthenticationError,
    ValidationError,
    ProcessingError,
    ResourceNotFoundError,
    RateLimitError,
)


class WaveQClient:
    """
    Main client for WaveQ AI Audio Agent SDK
    
    Example:
        >>> client = WaveQClient(api_key="your-api-key")
        >>> 
        >>> # Denoise audio
        >>> result = client.denoise_audio("noisy_audio.wav")
        >>> 
        >>> # Transcribe with diarization
        >>> result = client.transcribe_audio(
        ...     "meeting.mp3",
        ...     enable_diarization=True
        ... )
        >>> print(result.transcript)
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: float = 300.0,
        max_retries: int = 3,
    ):
        """
        Initialize WaveQ client
        
        Args:
            api_key: API authentication key
            base_url: Base URL of the WaveQ API server
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        self._client = httpx.Client(
            timeout=timeout,
            headers=self._get_headers(),
        )
        self._async_client = httpx.AsyncClient(
            timeout=timeout,
            headers=self._get_headers(),
        )
    
    def _get_headers(self) -> dict:
        """Get request headers with authentication"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "WaveQ-SDK/0.1.0",
        }
    
    def _handle_response(self, response: httpx.Response) -> dict:
        """Handle API response and raise appropriate exceptions"""
        if response.status_code == 401:
            raise AuthenticationError("Invalid or expired API key")
        elif response.status_code == 400:
            raise ValidationError(response.json().get("detail", "Validation error"))
        elif response.status_code == 404:
            raise ResourceNotFoundError(response.json().get("detail", "Resource not found"))
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(retry_after=int(retry_after) if retry_after else None)
        elif response.status_code >= 500:
            raise ProcessingError("Server error occurred")
        
        response.raise_for_status()
        return response.json()
    
    def _prepare_audio_file(
        self, 
        audio: Union[str, Path, BinaryIO, bytes]
    ) -> tuple[str, BinaryIO]:
        """Prepare audio file for upload"""
        if isinstance(audio, (str, Path)):
            file_path = Path(audio)
            if not file_path.exists():
                raise ValidationError(f"File not found: {audio}")
            return file_path.name, open(file_path, 'rb')
        elif isinstance(audio, bytes):
            return "audio.wav", audio
        else:
            return "audio.wav", audio
    
    def denoise_audio(
        self,
        audio: Union[str, Path, BinaryIO, bytes],
        noise_reduction_level: float = 0.8,
        enhance_speech: bool = True,
        callback_url: Optional[str] = None,
    ) -> AudioProcessingResponse:
        """
        Remove noise and enhance audio quality
        
        Args:
            audio: Audio file path, bytes, or file-like object
            noise_reduction_level: Noise reduction strength (0.0 to 1.0)
            enhance_speech: Whether to enhance speech frequencies
            callback_url: Optional webhook URL for async notifications
            
        Returns:
            AudioProcessingResponse with processed audio
        """
        filename, file_data = self._prepare_audio_file(audio)
        
        files = {"audio_file": (filename, file_data)}
        data = {
            "noise_reduction_level": noise_reduction_level,
            "enhance_speech": enhance_speech,
        }
        if callback_url:
            data["callback_url"] = callback_url
        
        response = self._client.post(
            f"{self.base_url}/api/v1/denoise",
            files=files,
            data=data,
        )
        
        result = self._handle_response(response)
        return AudioProcessingResponse(**result)
    
    def transcribe_audio(
        self,
        audio: Union[str, Path, BinaryIO, bytes],
        language: Optional[str] = None,
        enable_diarization: bool = False,
        timestamps: bool = True,
        model: str = "base",
        callback_url: Optional[str] = None,
    ) -> TranscriptionResponse:
        """
        Transcribe audio to text with optional speaker diarization
        
        Args:
            audio: Audio file path, bytes, or file-like object
            language: ISO language code (auto-detect if None)
            enable_diarization: Enable speaker diarization
            timestamps: Include word-level timestamps
            model: Whisper model size (tiny, base, small, medium, large)
            callback_url: Optional webhook URL for async notifications
            
        Returns:
            TranscriptionResponse with transcript and metadata
        """
        filename, file_data = self._prepare_audio_file(audio)
        
        files = {"audio_file": (filename, file_data)}
        data = {
            "enable_diarization": enable_diarization,
            "timestamps": timestamps,
            "model": model,
        }
        if language:
            data["language"] = language
        if callback_url:
            data["callback_url"] = callback_url
        
        response = self._client.post(
            f"{self.base_url}/api/v1/transcribe",
            files=files,
            data=data,
        )
        
        result = self._handle_response(response)
        return TranscriptionResponse(**result)
    
    def trim_audio(
        self,
        audio: Union[str, Path, BinaryIO, bytes],
        silence_threshold_db: float = -40.0,
        min_silence_duration: float = 0.5,
        remove_silence: bool = True,
        callback_url: Optional[str] = None,
    ) -> AudioProcessingResponse:
        """
        Smart trimming and silence removal
        
        Args:
            audio: Audio file path, bytes, or file-like object
            silence_threshold_db: Silence threshold in dB
            min_silence_duration: Minimum silence duration in seconds
            remove_silence: Whether to remove silence segments
            callback_url: Optional webhook URL for async notifications
            
        Returns:
            AudioProcessingResponse with trimmed audio
        """
        filename, file_data = self._prepare_audio_file(audio)
        
        files = {"audio_file": (filename, file_data)}
        data = {
            "silence_threshold_db": silence_threshold_db,
            "min_silence_duration": min_silence_duration,
            "remove_silence": remove_silence,
        }
        if callback_url:
            data["callback_url"] = callback_url
        
        response = self._client.post(
            f"{self.base_url}/api/v1/trim",
            files=files,
            data=data,
        )
        
        result = self._handle_response(response)
        return AudioProcessingResponse(**result)
    
    def separate_audio(
        self,
        audio: Union[str, Path, BinaryIO, bytes],
        separation_type: str = "vocals",
        model: str = "htdemucs",
        callback_url: Optional[str] = None,
    ) -> SeparationResponse:
        """
        Separate audio into different sources (vocals, drums, bass, etc.)
        
        Args:
            audio: Audio file path, bytes, or file-like object
            separation_type: Type of separation (vocals, drums, bass, other)
            model: Separation model to use
            callback_url: Optional webhook URL for async notifications
            
        Returns:
            SeparationResponse with separated audio tracks
        """
        filename, file_data = self._prepare_audio_file(audio)
        
        files = {"audio_file": (filename, file_data)}
        data = {
            "separation_type": separation_type,
            "model": model,
        }
        if callback_url:
            data["callback_url"] = callback_url
        
        response = self._client.post(
            f"{self.base_url}/api/v1/separate",
            files=files,
            data=data,
        )
        
        result = self._handle_response(response)
        return SeparationResponse(**result)
    
    def analyze_sentiment(
        self,
        audio: Union[str, Path, BinaryIO, bytes],
        include_emotions: bool = True,
        confidence_threshold: float = 0.5,
        callback_url: Optional[str] = None,
    ) -> SentimentResponse:
        """
        Analyze sentiment and emotions in audio
        
        Args:
            audio: Audio file path, bytes, or file-like object
            include_emotions: Include detailed emotion detection
            confidence_threshold: Minimum confidence for predictions
            callback_url: Optional webhook URL for async notifications
            
        Returns:
            SentimentResponse with sentiment analysis results
        """
        filename, file_data = self._prepare_audio_file(audio)
        
        files = {"audio_file": (filename, file_data)}
        data = {
            "include_emotions": include_emotions,
            "confidence_threshold": confidence_threshold,
        }
        if callback_url:
            data["callback_url"] = callback_url
        
        response = self._client.post(
            f"{self.base_url}/api/v1/sentiment",
            files=files,
            data=data,
        )
        
        result = self._handle_response(response)
        return SentimentResponse(**result)
    
    def text_to_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        language: str = "en",
        speed: float = 1.0,
        callback_url: Optional[str] = None,
    ) -> AudioProcessingResponse:
        """
        Convert text to speech with optional voice cloning
        
        Args:
            text: Text to convert to speech
            voice_id: Optional voice ID for cloning
            language: Language code
            speed: Speech speed multiplier (0.5 to 2.0)
            callback_url: Optional webhook URL for async notifications
            
        Returns:
            AudioProcessingResponse with generated speech
        """
        data = {
            "text": text,
            "language": language,
            "speed": speed,
        }
        if voice_id:
            data["voice_id"] = voice_id
        if callback_url:
            data["callback_url"] = callback_url
        
        response = self._client.post(
            f"{self.base_url}/api/v1/tts",
            json=data,
        )
        
        result = self._handle_response(response)
        return AudioProcessingResponse(**result)
    
    def get_task_status(self, task_id: str) -> AudioProcessingResponse:
        """
        Get the status of a processing task
        
        Args:
            task_id: Task identifier
            
        Returns:
            AudioProcessingResponse with current status
        """
        response = self._client.get(f"{self.base_url}/api/v1/tasks/{task_id}")
        result = self._handle_response(response)
        return AudioProcessingResponse(**result)
    
    def wait_for_completion(
        self,
        task_id: str,
        poll_interval: float = 2.0,
        max_wait: Optional[float] = None,
    ) -> AudioProcessingResponse:
        """
        Wait for a task to complete
        
        Args:
            task_id: Task identifier
            poll_interval: Time between status checks in seconds
            max_wait: Maximum time to wait in seconds (None for infinite)
            
        Returns:
            AudioProcessingResponse when task completes
            
        Raises:
            ProcessingError: If task fails or max_wait is exceeded
        """
        import time
        start_time = time.time()
        
        while True:
            status = self.get_task_status(task_id)
            
            if status.status == ProcessingStatus.COMPLETED:
                return status
            elif status.status == ProcessingStatus.FAILED:
                raise ProcessingError(
                    f"Task failed: {status.error}",
                    task_id=task_id
                )
            
            if max_wait and (time.time() - start_time) > max_wait:
                raise ProcessingError(
                    f"Task did not complete within {max_wait} seconds",
                    task_id=task_id
                )
            
            time.sleep(poll_interval)
    
    def close(self):
        """Close HTTP clients"""
        self._client.close()
    
    def __enter__(self):
        """Context manager support"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        self.close()
