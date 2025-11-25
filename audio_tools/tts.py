"""
Text-to-Speech and Voice Cloning
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
import torch
import torchaudio

logger = logging.getLogger(__name__)


class TextToSpeech:
    """
    Text-to-speech conversion with optional voice cloning
    
    Supports multiple TTS backends including local models and cloud APIs.
    """
    
    def __init__(self, backend: str = "bark", device: str = "cpu"):
        """
        Initialize TTS engine
        
        Args:
            backend: TTS backend (bark, coqui, elevenlabs, openai)
            device: Device to run on (cpu or cuda)
        """
        self.backend = backend
        self.device = device
        self.model = None
        logger.info(f"TTS initialized with backend: {backend}")
    
    def _load_model(self):
        """Lazy load TTS model"""
        if self.model is None and self.backend == "bark":
            logger.info("Loading Bark TTS model...")
            try:
                from transformers import AutoProcessor, BarkModel
                
                self.processor = AutoProcessor.from_pretrained("suno/bark-small")
                self.model = BarkModel.from_pretrained("suno/bark-small")
                self.model.to(self.device)
                
            except Exception as e:
                logger.error(f"Failed to load Bark model: {e}")
                self.model = None
    
    def synthesize(
        self,
        text: str,
        output_path: Path,
        voice_id: Optional[str] = None,
        language: str = "en",
        speed: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Convert text to speech
        
        Args:
            text: Text to convert
            output_path: Path to save audio
            voice_id: Optional voice preset or cloning ID
            language: Language code
            speed: Speech speed multiplier
            
        Returns:
            Dictionary with synthesis results
        """
        try:
            logger.info(f"Synthesizing speech: {text[:50]}...")
            
            if self.backend == "bark":
                return self._synthesize_bark(text, output_path, voice_id)
            elif self.backend == "elevenlabs":
                return self._synthesize_elevenlabs(text, output_path, voice_id)
            elif self.backend == "openai":
                return self._synthesize_openai(text, output_path, voice_id)
            else:
                raise ValueError(f"Unknown backend: {self.backend}")
            
        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
            }
    
    def _synthesize_bark(
        self,
        text: str,
        output_path: Path,
        voice_preset: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Synthesize using Bark (local model)"""
        self._load_model()
        
        if self.model is None:
            return {
                "status": "failed",
                "error": "Bark model not loaded",
            }
        
        # Use default voice preset if not specified
        if voice_preset is None:
            voice_preset = "v2/en_speaker_6"
        
        # Process text
        inputs = self.processor(text, voice_preset=voice_preset, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate audio
        with torch.no_grad():
            audio_array = self.model.generate(**inputs)
        
        # Convert to proper format
        audio_array = audio_array.cpu().numpy().squeeze()
        
        # Save audio
        sample_rate = self.model.generation_config.sample_rate
        torchaudio.save(
            str(output_path),
            torch.from_numpy(audio_array).unsqueeze(0),
            sample_rate,
        )
        
        logger.info(f"Speech saved to: {output_path}")
        
        return {
            "status": "success",
            "output_path": str(output_path),
            "backend": "bark",
            "voice_preset": voice_preset,
            "sample_rate": sample_rate,
            "duration_seconds": len(audio_array) / sample_rate,
        }
    
    def _synthesize_elevenlabs(
        self,
        text: str,
        output_path: Path,
        voice_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Synthesize using ElevenLabs API"""
        try:
            from elevenlabs import generate, save, voices
            from config import settings
            
            if not settings.ELEVENLABS_API_KEY:
                return {
                    "status": "failed",
                    "error": "ElevenLabs API key not configured",
                }
            
            # Use default voice if not specified
            if voice_id is None:
                voice_id = "EXAVITQu4vr4xnSDxMaL"  # Bella voice
            
            # Generate audio
            audio = generate(
                text=text,
                voice=voice_id,
                model="eleven_monolingual_v1",
            )
            
            # Save
            save(audio, str(output_path))
            
            return {
                "status": "success",
                "output_path": str(output_path),
                "backend": "elevenlabs",
                "voice_id": voice_id,
            }
            
        except ImportError:
            return {
                "status": "failed",
                "error": "elevenlabs package not installed",
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": f"ElevenLabs API error: {str(e)}",
            }
    
    def _synthesize_openai(
        self,
        text: str,
        output_path: Path,
        voice: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Synthesize using OpenAI TTS API"""
        try:
            from openai import OpenAI
            from config import settings
            
            if not settings.OPENAI_API_KEY:
                return {
                    "status": "failed",
                    "error": "OpenAI API key not configured",
                }
            
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Use default voice if not specified
            if voice is None:
                voice = "alloy"
            
            # Generate speech
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
            )
            
            # Save
            response.stream_to_file(str(output_path))
            
            return {
                "status": "success",
                "output_path": str(output_path),
                "backend": "openai",
                "voice": voice,
            }
            
        except ImportError:
            return {
                "status": "failed",
                "error": "openai package not installed",
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": f"OpenAI API error: {str(e)}",
            }
    
    def get_available_voices(self) -> list:
        """Get list of available voices for the current backend"""
        if self.backend == "bark":
            # Bark voice presets
            return [
                "v2/en_speaker_0",
                "v2/en_speaker_1",
                "v2/en_speaker_2",
                "v2/en_speaker_3",
                "v2/en_speaker_4",
                "v2/en_speaker_5",
                "v2/en_speaker_6",
                "v2/en_speaker_7",
                "v2/en_speaker_8",
                "v2/en_speaker_9",
            ]
        elif self.backend == "openai":
            return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        else:
            return []
