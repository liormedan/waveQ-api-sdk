"""
WaveQ - AI Audio Agent SDK

A comprehensive Python SDK for AI-powered audio processing including:
- Audio denoising and enhancement
- Speech-to-text with speaker diarization
- Smart trimming and silence removal
- Source separation (vocals/music)
- Audio sentiment analysis
- Advanced text-to-speech and voice cloning

Example:
    >>> from waveq import WaveQClient
    >>> client = WaveQClient(api_key="your-api-key")
    >>> result = client.denoise_audio("input.wav")
    >>> print(result.output_url)
"""

__version__ = "0.1.0"
__author__ = "WaveQ Team"
__license__ = "MIT"

# Import main client for easy access
from waveq.client import WaveQClient
from waveq.models import (
    AudioProcessingRequest,
    AudioProcessingResponse,
    ProcessingStatus,
    AudioFormat,
)
from waveq.exceptions import (
    WaveQException,
    AuthenticationError,
    ValidationError,
    ProcessingError,
)

__all__ = [
    "WaveQClient",
    "AudioProcessingRequest",
    "AudioProcessingResponse",
    "ProcessingStatus",
    "AudioFormat",
    "WaveQException",
    "AuthenticationError",
    "ValidationError",
    "ProcessingError",
]
