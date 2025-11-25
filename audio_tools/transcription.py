"""
Speech-to-Text and Speaker Diarization using OpenAI Whisper
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import whisper
import torch

logger = logging.getLogger(__name__)


class AudioTranscriber:
    """
    AI-powered speech-to-text transcription with speaker diarization
    
    Uses OpenAI Whisper for highly accurate transcription across
    multiple languages with optional speaker identification.
    """
    
    def __init__(self, model_name: str = "base", device: str = "cpu"):
        """
        Initialize the transcriber
        
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            device: Device to run on (cpu or cuda)
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        logger.info(f"Transcriber initialized with model: {model_name}")
    
    def _load_model(self):
        """Lazy load the Whisper model"""
        if self.model is None:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name, device=self.device)
    
    def transcribe(
        self,
        audio_path: Path,
        language: Optional[str] = None,
        enable_diarization: bool = False,
        timestamps: bool = True,
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text
        
        Args:
            audio_path: Path to audio file
            language: ISO language code (auto-detect if None)
            enable_diarization: Enable speaker diarization
            timestamps: Include word-level timestamps
            
        Returns:
            Dictionary with transcript and metadata
        """
        try:
            logger.info(f"Transcribing audio: {audio_path}")
            
            # Load model if not already loaded
            self._load_model()
            
            # Transcribe
            options = {
                "language": language,
                "task": "transcribe",
                "verbose": False,
            }
            
            if timestamps:
                options["word_timestamps"] = True
            
            result = self.model.transcribe(str(audio_path), **options)
            
            # Extract text and segments
            transcript = result["text"]
            segments = result.get("segments", [])
            detected_language = result.get("language", language)
            
            # Format segments with timestamps
            formatted_segments = []
            for seg in segments:
                formatted_seg = {
                    "start": seg["start"],
                    "end": seg["end"],
                    "text": seg["text"].strip(),
                }
                
                if "words" in seg and timestamps:
                    formatted_seg["words"] = [
                        {
                            "word": w["word"],
                            "start": w["start"],
                            "end": w["end"],
                            "probability": w.get("probability", 0.0),
                        }
                        for w in seg["words"]
                    ]
                
                formatted_segments.append(formatted_seg)
            
            # Speaker diarization (simplified version)
            speakers = None
            if enable_diarization:
                speakers = self._perform_diarization(formatted_segments)
            
            logger.info(f"Transcription completed. Language: {detected_language}")
            
            return {
                "status": "success",
                "transcript": transcript.strip(),
                "segments": formatted_segments,
                "language": detected_language,
                "speakers": speakers,
                "duration_seconds": segments[-1]["end"] if segments else 0,
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
            }
    
    def _perform_diarization(self, segments: List[Dict]) -> List[str]:
        """
        Perform simple speaker diarization
        
        Note: This is a simplified version. For production, use
        pyannote.audio or similar libraries.
        
        Args:
            segments: Transcription segments
            
        Returns:
            List of speaker labels
        """
        # Simplified: Assign speakers based on silence gaps
        # In production, use embeddings-based clustering
        speakers = []
        current_speaker = "Speaker_1"
        speaker_count = 1
        
        for i, seg in enumerate(segments):
            # If there's a long pause (>2s), assume speaker change
            if i > 0:
                gap = seg["start"] - segments[i-1]["end"]
                if gap > 2.0:
                    speaker_count += 1
                    current_speaker = f"Speaker_{speaker_count}"
            
            speakers.append(current_speaker)
            seg["speaker"] = current_speaker
        
        unique_speakers = list(set(speakers))
        logger.info(f"Detected {len(unique_speakers)} speakers")
        
        return unique_speakers
    
    def get_transcript_with_speakers(self, result: Dict[str, Any]) -> str:
        """
        Format transcript with speaker labels
        
        Args:
            result: Transcription result dictionary
            
        Returns:
            Formatted transcript string
        """
        if not result.get("speakers") or not result.get("segments"):
            return result.get("transcript", "")
        
        formatted_lines = []
        current_speaker = None
        current_text = []
        
        for seg in result["segments"]:
            speaker = seg.get("speaker", "Unknown")
            
            if speaker != current_speaker:
                if current_text:
                    formatted_lines.append(
                        f"{current_speaker}: {' '.join(current_text)}"
                    )
                    current_text = []
                current_speaker = speaker
            
            current_text.append(seg["text"])
        
        # Add final segment
        if current_text:
            formatted_lines.append(
                f"{current_speaker}: {' '.join(current_text)}"
            )
        
        return "\n".join(formatted_lines)
