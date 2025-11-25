"""
Audio Source Separation (Vocals/Music) using Demucs
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
import torch
import torchaudio
from demucs.pretrained import get_model
from demucs.apply import apply_model
import numpy as np

logger = logging.getLogger(__name__)


class AudioSeparator:
    """
    AI-powered source separation for isolating vocals, drums, bass, and other instruments
    
    Uses Demucs (Deep Extractor for Music Sources) for high-quality
    audio source separation.
    """
    
    def __init__(self, model_name: str = "htdemucs", device: str = "cpu"):
        """
        Initialize the separator
        
        Args:
            model_name: Demucs model name (htdemucs, htdemucs_ft, mdx_extra)
            device: Device to run on (cpu or cuda)
        """
        self.model_name = model_name
        self.device = device
        self.model = None
        logger.info(f"Separator initialized with model: {model_name}")
    
    def _load_model(self):
        """Lazy load the Demucs model"""
        if self.model is None:
            logger.info(f"Loading Demucs model: {self.model_name}")
            self.model = get_model(self.model_name)
            self.model.to(self.device)
            self.model.eval()
    
    def separate(
        self,
        input_path: Path,
        output_dir: Path,
        separation_type: str = "vocals",
        save_all_stems: bool = False,
    ) -> Dict[str, Any]:
        """
        Separate audio into different sources
        
        Args:
            input_path: Path to input audio
            output_dir: Directory to save separated stems
            separation_type: Type of separation (vocals, drums, bass, other)
            save_all_stems: Save all stems or just the requested one
            
        Returns:
            Dictionary with separated audio paths
        """
        try:
            logger.info(f"Separating audio: {input_path}")
            
            # Load model if not already loaded
            self._load_model()
            
            # Load audio
            wav, sr = torchaudio.load(str(input_path))
            
            # Resample if needed (Demucs expects 44.1kHz)
            if sr != self.model.samplerate:
                logger.info(f"Resampling from {sr}Hz to {self.model.samplerate}Hz")
                resampler = torchaudio.transforms.Resample(sr, self.model.samplerate)
                wav = resampler(wav)
                sr = self.model.samplerate
            
            # Ensure correct shape (channels, samples)
            if wav.shape[0] == 1:
                # Mono to stereo
                wav = wav.repeat(2, 1)
            
            # Move to device
            wav = wav.to(self.device)
            
            # Apply model
            logger.info("Running source separation...")
            with torch.no_grad():
                sources = apply_model(
                    self.model,
                    wav.unsqueeze(0),
                    device=self.device,
                    shifts=1,
                    split=True,
                    overlap=0.25,
                    progress=False,
                )[0]
            
            # Demucs outputs: drums, bass, other, vocals
            source_names = ["drums", "bass", "other", "vocals"]
            
            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save stems
            output_files = {}
            for i, source_name in enumerate(source_names):
                # Save requested stem or all stems if specified
                if save_all_stems or source_name == separation_type:
                    output_file = output_dir / f"{input_path.stem}_{source_name}.wav"
                    
                    # Get source audio
                    source_audio = sources[i].cpu()
                    
                    # Save
                    torchaudio.save(
                        str(output_file),
                        source_audio,
                        sr,
                    )
                    
                    output_files[source_name] = str(output_file)
                    logger.info(f"Saved {source_name} to: {output_file}")
            
            return {
                "status": "success",
                "separated_tracks": output_files,
                "model": self.model_name,
                "sample_rate": sr,
            }
            
        except Exception as e:
            logger.error(f"Separation failed: {e}", exc_info=True)
            return {
                "status": "failed",
                "error": str(e),
            }
    
    def get_available_sources(self) -> List[str]:
        """
        Get list of available source types
        
        Returns:
            List of source names
        """
        return ["vocals", "drums", "bass", "other"]
