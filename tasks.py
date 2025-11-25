"""
Celery tasks for async audio processing
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
from celery import Task
from celery_app import celery_app
from audio_tools import (
    AudioDenoiser,
    AudioTranscriber,
    AudioTrimmer,
    AudioSeparator,
    SentimentAnalyzer,
    TextToSpeech,
)
from config import settings
import httpx

logger = logging.getLogger(__name__)


class CallbackTask(Task):
    """Base task with callback support"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called when task succeeds"""
        callback_url = kwargs.get("callback_url")
        if callback_url:
            send_webhook_notification(callback_url, {
                "task_id": task_id,
                "status": "completed",
                "result": retval,
            })
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when task fails"""
        callback_url = kwargs.get("callback_url")
        if callback_url:
            send_webhook_notification(callback_url, {
                "task_id": task_id,
                "status": "failed",
                "error": str(exc),
            })


def send_webhook_notification(callback_url: str, data: Dict[str, Any]) -> bool:
    """
    Send webhook notification to callback URL
    
    Args:
        callback_url: URL to send notification to
        data: Data to send in POST request
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Sending webhook to {callback_url}")
        
        response = httpx.post(
            callback_url,
            json=data,
            timeout=10.0,
            headers={"Content-Type": "application/json"},
        )
        
        response.raise_for_status()
        logger.info(f"Webhook sent successfully to {callback_url}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send webhook to {callback_url}: {e}")
        return False


@celery_app.task(base=CallbackTask, bind=True, name="tasks.process_denoise")
def process_denoise(
    self,
    task_id: str,
    input_path: str,
    output_path: str,
    noise_reduction_level: float = 0.8,
    enhance_speech: bool = True,
    callback_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Async task for audio denoising
    
    Args:
        task_id: Task identifier
        input_path: Path to input audio
        output_path: Path to save output
        noise_reduction_level: Noise reduction strength
        enhance_speech: Enable speech enhancement
        callback_url: Optional webhook URL
        
    Returns:
        Processing result dictionary
    """
    logger.info(f"Task {task_id}: Starting denoise processing")
    
    denoiser = AudioDenoiser()
    result = denoiser.denoise(
        input_path=Path(input_path),
        output_path=Path(output_path),
        noise_reduction_level=noise_reduction_level,
        enhance_speech=enhance_speech,
    )
    
    result["task_id"] = task_id
    return result


@celery_app.task(base=CallbackTask, bind=True, name="tasks.process_transcribe")
def process_transcribe(
    self,
    task_id: str,
    input_path: str,
    language: Optional[str] = None,
    enable_diarization: bool = False,
    timestamps: bool = True,
    model: str = "base",
    callback_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Async task for audio transcription"""
    logger.info(f"Task {task_id}: Starting transcription")
    
    transcriber = AudioTranscriber(model_name=model, device=settings.WHISPER_DEVICE)
    result = transcriber.transcribe(
        audio_path=Path(input_path),
        language=language,
        enable_diarization=enable_diarization,
        timestamps=timestamps,
    )
    
    result["task_id"] = task_id
    return result


@celery_app.task(base=CallbackTask, bind=True, name="tasks.process_trim")
def process_trim(
    self,
    task_id: str,
    input_path: str,
    output_path: str,
    silence_threshold_db: float = -40.0,
    min_silence_duration: float = 0.5,
    remove_silence: bool = True,
    callback_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Async task for audio trimming"""
    logger.info(f"Task {task_id}: Starting trimming")
    
    trimmer = AudioTrimmer()
    result = trimmer.trim(
        input_path=Path(input_path),
        output_path=Path(output_path),
        silence_threshold_db=silence_threshold_db,
        min_silence_duration=min_silence_duration,
        remove_silence=remove_silence,
    )
    
    result["task_id"] = task_id
    return result


@celery_app.task(base=CallbackTask, bind=True, name="tasks.process_separate")
def process_separate(
    self,
    task_id: str,
    input_path: str,
    output_dir: str,
    separation_type: str = "vocals",
    save_all_stems: bool = False,
    callback_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Async task for source separation"""
    logger.info(f"Task {task_id}: Starting source separation")
    
    separator = AudioSeparator(
        model_name=settings.DEMUCS_MODEL,
        device=settings.DEMUCS_DEVICE,
    )
    result = separator.separate(
        input_path=Path(input_path),
        output_dir=Path(output_dir),
        separation_type=separation_type,
        save_all_stems=save_all_stems,
    )
    
    result["task_id"] = task_id
    return result


@celery_app.task(base=CallbackTask, bind=True, name="tasks.process_sentiment")
def process_sentiment(
    self,
    task_id: str,
    input_path: str,
    include_emotions: bool = True,
    confidence_threshold: float = 0.5,
    callback_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Async task for sentiment analysis"""
    logger.info(f"Task {task_id}: Starting sentiment analysis")
    
    analyzer = SentimentAnalyzer(device=settings.WHISPER_DEVICE)
    result = analyzer.analyze(
        audio_path=Path(input_path),
        include_emotions=include_emotions,
        confidence_threshold=confidence_threshold,
    )
    
    result["task_id"] = task_id
    return result


@celery_app.task(base=CallbackTask, bind=True, name="tasks.process_tts")
def process_tts(
    self,
    task_id: str,
    text: str,
    output_path: str,
    voice_id: Optional[str] = None,
    language: str = "en",
    speed: float = 1.0,
    backend: str = "bark",
    callback_url: Optional[str] = None,
) -> Dict[str, Any]:
    """Async task for text-to-speech"""
    logger.info(f"Task {task_id}: Starting TTS synthesis")
    
    tts = TextToSpeech(backend=backend, device=settings.WHISPER_DEVICE)
    result = tts.synthesize(
        text=text,
        output_path=Path(output_path),
        voice_id=voice_id,
        language=language,
        speed=speed,
    )
    
    result["task_id"] = task_id
    return result


@celery_app.task(name="tasks.cleanup_old_files")
def cleanup_old_files(max_age_hours: int = 24):
    """
    Periodic task to cleanup old uploaded/processed files
    
    Args:
        max_age_hours: Maximum age of files to keep in hours
    """
    import time
    from datetime import datetime, timedelta
    
    cutoff_time = time.time() - (max_age_hours * 3600)
    cleaned_count = 0
    
    for directory in [settings.UPLOAD_DIR, settings.OUTPUT_DIR]:
        if not directory.exists():
            continue
            
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    cleaned_count += 1
                    logger.info(f"Deleted old file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete {file_path}: {e}")
    
    logger.info(f"Cleanup completed. Deleted {cleaned_count} files.")
    return {"cleaned_files": cleaned_count}
