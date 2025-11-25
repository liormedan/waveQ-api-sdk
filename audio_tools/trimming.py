"""
Smart Audio Trimming and Silence Removal
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple
import numpy as np
import soundfile as sf
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

logger = logging.getLogger(__name__)


class AudioTrimmer:
    """
    Smart audio trimming and silence removal
    
    Automatically detects and removes silence while preserving
    important audio content.
    """
    
    def __init__(self):
        """Initialize the trimmer"""
        pass
    
    def trim(
        self,
        input_path: Path,
        output_path: Path,
        silence_threshold_db: float = -40.0,
        min_silence_duration: float = 0.5,
        remove_silence: bool = True,
        padding_ms: int = 100,
    ) -> Dict[str, Any]:
        """
        Trim audio and remove silence
        
        Args:
            input_path: Path to input audio
            output_path: Path to save trimmed audio
            silence_threshold_db: Silence threshold in dB
            min_silence_duration: Minimum silence duration in seconds
            remove_silence: Whether to remove silence segments
            padding_ms: Padding to keep around non-silent segments
            
        Returns:
            Dictionary with processing results
        """
        try:
            logger.info(f"Trimming audio: {input_path}")
            
            # Load audio using pydub
            audio = AudioSegment.from_file(str(input_path))
            original_duration = len(audio) / 1000.0  # Convert to seconds
            
            if remove_silence:
                # Detect non-silent chunks
                min_silence_len = int(min_silence_duration * 1000)  # Convert to ms
                
                nonsilent_ranges = detect_nonsilent(
                    audio,
                    min_silence_len=min_silence_len,
                    silence_thresh=silence_threshold_db,
                    seek_step=10,
                )
                
                if not nonsilent_ranges:
                    logger.warning("No non-silent audio detected")
                    return {
                        "status": "failed",
                        "error": "No non-silent audio detected",
                    }
                
                # Combine non-silent segments with padding
                trimmed_audio = AudioSegment.empty()
                for start_ms, end_ms in nonsilent_ranges:
                    # Add padding
                    start_ms = max(0, start_ms - padding_ms)
                    end_ms = min(len(audio), end_ms + padding_ms)
                    
                    segment = audio[start_ms:end_ms]
                    trimmed_audio += segment
                
                # Save trimmed audio
                trimmed_audio.export(str(output_path), format=output_path.suffix[1:])
                
                final_duration = len(trimmed_audio) / 1000.0
                silence_removed = original_duration - final_duration
                
                logger.info(
                    f"Trimmed {silence_removed:.2f}s of silence "
                    f"({(silence_removed/original_duration)*100:.1f}%)"
                )
                
                return {
                    "status": "success",
                    "output_path": str(output_path),
                    "original_duration_seconds": original_duration,
                    "trimmed_duration_seconds": final_duration,
                    "silence_removed_seconds": silence_removed,
                    "reduction_percentage": (silence_removed / original_duration) * 100,
                    "segments_kept": len(nonsilent_ranges),
                }
            
            else:
                # Just trim leading/trailing silence
                trimmed = self._trim_edges(
                    audio,
                    silence_threshold_db,
                    padding_ms
                )
                
                trimmed.export(str(output_path), format=output_path.suffix[1:])
                
                final_duration = len(trimmed) / 1000.0
                
                return {
                    "status": "success",
                    "output_path": str(output_path),
                    "original_duration_seconds": original_duration,
                    "trimmed_duration_seconds": final_duration,
                    "edge_trimming_only": True,
                }
            
        except Exception as e:
            logger.error(f"Trimming failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
            }
    
    def _trim_edges(
        self,
        audio: AudioSegment,
        silence_thresh: float,
        padding_ms: int,
    ) -> AudioSegment:
        """
        Trim silence from beginning and end only
        
        Args:
            audio: Audio segment
            silence_thresh: Silence threshold in dB
            padding_ms: Padding to keep
            
        Returns:
            Trimmed audio segment
        """
        # Find first non-silent sample
        start_trim = self._detect_leading_silence(audio, silence_thresh)
        
        # Find last non-silent sample
        end_trim = self._detect_leading_silence(audio.reverse(), silence_thresh)
        
        # Apply padding
        start_trim = max(0, start_trim - padding_ms)
        end_trim = max(0, end_trim - padding_ms)
        
        duration = len(audio)
        return audio[start_trim:duration - end_trim]
    
    def _detect_leading_silence(
        self,
        audio: AudioSegment,
        silence_threshold: float,
        chunk_size: int = 10,
    ) -> int:
        """
        Detect leading silence in audio
        
        Args:
            audio: Audio segment
            silence_threshold: Threshold in dB
            chunk_size: Size of chunks to analyze in ms
            
        Returns:
            Duration of leading silence in ms
        """
        trim_ms = 0
        
        while trim_ms < len(audio):
            chunk = audio[trim_ms:trim_ms + chunk_size]
            if chunk.dBFS > silence_threshold:
                break
            trim_ms += chunk_size
        
        return trim_ms
