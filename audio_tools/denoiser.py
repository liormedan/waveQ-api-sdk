"""
AI Denoising and Audio Enhancement Module
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
import numpy as np
import soundfile as sf
import noisereduce as nr

logger = logging.getLogger(__name__)


class AudioDenoiser:
    """
    AI-powered audio denoising and enhancement
    
    Uses noise reduction algorithms and spectral gating to remove
    unwanted background noise while preserving audio quality.
    """
    
    def __init__(self):
        """Initialize the denoiser"""
        self.sample_rate = 16000
    
    def denoise(
        self,
        input_path: Path,
        output_path: Path,
        noise_reduction_level: float = 0.8,
        enhance_speech: bool = True,
    ) -> Dict[str, Any]:
        """
        Remove noise from audio file
        
        Args:
            input_path: Path to input audio file
            output_path: Path to save denoised audio
            noise_reduction_level: Strength of noise reduction (0.0 to 1.0)
            enhance_speech: Whether to enhance speech frequencies
            
        Returns:
            Dictionary with processing results and metadata
        """
        try:
            logger.info(f"Denoising audio: {input_path}")
            
            # Load audio
            audio_data, sample_rate = sf.read(str(input_path))
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Apply noise reduction
            # Use first 1 second as noise profile (or detect silence)
            noise_sample_duration = min(1.0, len(audio_data) / sample_rate / 10)
            noise_sample_length = int(noise_sample_duration * sample_rate)
            
            reduced_noise = nr.reduce_noise(
                y=audio_data,
                sr=sample_rate,
                stationary=True,
                prop_decrease=noise_reduction_level,
            )
            
            # Speech enhancement (optional)
            if enhance_speech:
                # Apply high-pass filter to remove low-frequency rumble
                from scipy.signal import butter, filtfilt
                
                nyquist = sample_rate / 2
                low_cutoff = 80 / nyquist  # Remove frequencies below 80Hz
                b, a = butter(4, low_cutoff, btype='high')
                reduced_noise = filtfilt(b, a, reduced_noise)
                
                logger.info("Applied speech enhancement")
            
            # Normalize audio
            max_val = np.max(np.abs(reduced_noise))
            if max_val > 0:
                reduced_noise = reduced_noise / max_val * 0.95
            
            # Save output
            sf.write(str(output_path), reduced_noise, sample_rate)
            
            logger.info(f"Denoised audio saved to: {output_path}")
            
            return {
                "status": "success",
                "output_path": str(output_path),
                "duration_seconds": len(reduced_noise) / sample_rate,
                "sample_rate": sample_rate,
                "noise_reduction_level": noise_reduction_level,
                "enhanced": enhance_speech,
            }
            
        except Exception as e:
            logger.error(f"Denoising failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
            }
    
    def analyze_noise_profile(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """
        Analyze noise characteristics in audio
        
        Args:
            audio_data: Audio signal as numpy array
            sample_rate: Sample rate in Hz
            
        Returns:
            Dictionary with noise analysis results
        """
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio_data ** 2))
        
        # Calculate SNR estimate
        signal_power = np.mean(audio_data ** 2)
        noise_power = np.var(audio_data[:int(sample_rate)])  # Use first second as noise estimate
        snr = 10 * np.log10(signal_power / (noise_power + 1e-10))
        
        return {
            "rms_energy": float(rms),
            "estimated_snr_db": float(snr),
            "duration_seconds": len(audio_data) / sample_rate,
        }
