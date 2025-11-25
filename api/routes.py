"""
API Routes for audio processing endpoints
"""

from fastapi import APIRouter, File, UploadFile, Form, BackgroundTasks, Depends
from typing import Optional
import logging

from waveq.models import (
    AudioProcessingResponse,
    TranscriptionResponse,
    SeparationResponse,
    SentimentResponse,
    ProcessingStatus,
)
from config import settings
from utils import generate_task_id, async_save_upload_file
from api.auth import verify_api_key
from tasks import (
    process_denoise,
    process_transcribe,
    process_trim,
    process_separate,
    process_sentiment,
    process_tts,
)

logger = logging.getLogger(__name__)

router = APIRouter()


# In-memory task storage (replace with database in production)
tasks_db = {}

# Check if Celery is available
try:
    from celery_app import celery_app
    CELERY_ENABLED = True
    logger.info("Celery enabled for async processing")
except ImportError:
    CELERY_ENABLED = False
    logger.warning("Celery not available, using synchronous processing")


@router.post("/denoise", response_model=AudioProcessingResponse)
async def denoise_audio(
    audio_file: UploadFile = File(...),
    noise_reduction_level: float = Form(0.8),
    enhance_speech: bool = Form(True),
    callback_url: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
    api_key: str = Depends(verify_api_key),
):
    """
    Remove noise and enhance audio quality
    """
    task_id = generate_task_id()
    
    # Save uploaded file
    file_path = await async_save_upload_file(
        audio_file.file,
        audio_file.filename,
        settings.UPLOAD_DIR
    )
    
    logger.info(f"Task {task_id}: Denoising audio file {audio_file.filename}")
    
    # Create task record
    task = AudioProcessingResponse(
        task_id=task_id,
        status=ProcessingStatus.PENDING,
        metadata={
            "operation": "denoise",
            "filename": audio_file.filename,
            "file_path": str(file_path),
            "noise_reduction_level": noise_reduction_level,
            "enhance_speech": enhance_speech,
        }
    )
    
    tasks_db[task_id] = task
    
    # Queue async task if Celery is available
    if CELERY_ENABLED:
        output_path = settings.OUTPUT_DIR / f"{task_id}_denoised.wav"
        process_denoise.delay(
            task_id=task_id,
            input_path=str(file_path),
            output_path=str(output_path),
            noise_reduction_level=noise_reduction_level,
            enhance_speech=enhance_speech,
            callback_url=callback_url,
        )
        task.status = ProcessingStatus.PROCESSING
        logger.info(f"Task {task_id} queued for async processing")
    else:
        logger.warning(f"Task {task_id} created but not processed (Celery disabled)")
    
    return task


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: Optional[str] = Form(None),
    enable_diarization: bool = Form(False),
    timestamps: bool = Form(True),
    model: str = Form("base"),
    callback_url: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
    api_key: str = Depends(verify_api_key),
):
    """
    Transcribe audio to text with optional speaker diarization
    """
    task_id = generate_task_id()
    
    file_path = await async_save_upload_file(
        audio_file.file,
        audio_file.filename,
        settings.UPLOAD_DIR
    )
    
    logger.info(f"Task {task_id}: Transcribing audio file {audio_file.filename}")
    
    task = TranscriptionResponse(
        task_id=task_id,
        status=ProcessingStatus.PENDING,
        metadata={
            "operation": "transcribe",
            "filename": audio_file.filename,
            "file_path": str(file_path),
            "language": language,
            "enable_diarization": enable_diarization,
            "model": model,
        }
    )
    
    tasks_db[task_id] = task
    
    # Queue async task if Celery is available
    if CELERY_ENABLED:
        process_transcribe.delay(
            task_id=task_id,
            input_path=str(file_path),
            language=language,
            enable_diarization=enable_diarization,
            timestamps=timestamps,
            model=model,
            callback_url=callback_url,
        )
        task.status = ProcessingStatus.PROCESSING
    
    return task


@router.post("/trim", response_model=AudioProcessingResponse)
async def trim_audio(
    audio_file: UploadFile = File(...),
    silence_threshold_db: float = Form(-40.0),
    min_silence_duration: float = Form(0.5),
    remove_silence: bool = Form(True),
    callback_url: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
    api_key: str = Depends(verify_api_key),
):
    """
    Smart trimming and silence removal
    """
    task_id = generate_task_id()
    
    file_path = await async_save_upload_file(
        audio_file.file,
        audio_file.filename,
        settings.UPLOAD_DIR
    )
    
    logger.info(f"Task {task_id}: Trimming audio file {audio_file.filename}")
    
    task = AudioProcessingResponse(
        task_id=task_id,
        status=ProcessingStatus.PENDING,
        metadata={
            "operation": "trim",
            "filename": audio_file.filename,
            "file_path": str(file_path),
            "silence_threshold_db": silence_threshold_db,
            "min_silence_duration": min_silence_duration,
        }
    )
    
    tasks_db[task_id] = task
    
    return task


@router.post("/separate", response_model=SeparationResponse)
async def separate_audio(
    audio_file: UploadFile = File(...),
    separation_type: str = Form("vocals"),
    model: str = Form("htdemucs"),
    callback_url: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
    api_key: str = Depends(verify_api_key),
):
    """
    Separate audio into different sources (vocals, drums, bass, etc.)
    """
    task_id = generate_task_id()
    
    file_path = await async_save_upload_file(
        audio_file.file,
        audio_file.filename,
        settings.UPLOAD_DIR
    )
    
    logger.info(f"Task {task_id}: Separating audio file {audio_file.filename}")
    
    task = SeparationResponse(
        task_id=task_id,
        status=ProcessingStatus.PENDING,
        metadata={
            "operation": "separate",
            "filename": audio_file.filename,
            "file_path": str(file_path),
            "separation_type": separation_type,
            "model": model,
        }
    )
    
    tasks_db[task_id] = task
    
    return task


@router.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(
    audio_file: UploadFile = File(...),
    include_emotions: bool = Form(True),
    confidence_threshold: float = Form(0.5),
    callback_url: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
    api_key: str = Depends(verify_api_key),
):
    """
    Analyze sentiment and emotions in audio
    """
    task_id = generate_task_id()
    
    file_path = await async_save_upload_file(
        audio_file.file,
        audio_file.filename,
        settings.UPLOAD_DIR
    )
    
    logger.info(f"Task {task_id}: Analyzing sentiment of {audio_file.filename}")
    
    task = SentimentResponse(
        task_id=task_id,
        status=ProcessingStatus.PENDING,
        metadata={
            "operation": "sentiment",
            "filename": audio_file.filename,
            "file_path": str(file_path),
            "include_emotions": include_emotions,
            "confidence_threshold": confidence_threshold,
        }
    )
    
    tasks_db[task_id] = task
    
    return task


@router.post("/tts", response_model=AudioProcessingResponse)
async def text_to_speech(
    text: str = Form(...),
    voice_id: Optional[str] = Form(None),
    language: str = Form("en"),
    speed: float = Form(1.0),
    callback_url: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None,
    api_key: str = Depends(verify_api_key),
):
    """
    Convert text to speech with optional voice cloning
    """
    task_id = generate_task_id()
    
    logger.info(f"Task {task_id}: Generating speech from text")
    
    task = AudioProcessingResponse(
        task_id=task_id,
        status=ProcessingStatus.PENDING,
        metadata={
            "operation": "tts",
            "text": text[:100] + "..." if len(text) > 100 else text,
            "voice_id": voice_id,
            "language": language,
            "speed": speed,
        }
    )
    
    tasks_db[task_id] = task
    
    return task


@router.get("/tasks/{task_id}", response_model=AudioProcessingResponse)
async def get_task_status(
    task_id: str,
    api_key: str = Depends(verify_api_key),
):
    """
    Get the status of a processing task
    """
    from waveq.exceptions import ResourceNotFoundError
    
    if task_id not in tasks_db:
        raise ResourceNotFoundError(f"Task not found: {task_id}")
    
    return tasks_db[task_id]


@router.delete("/tasks/{task_id}")
async def cancel_task(
    task_id: str,
    api_key: str = Depends(verify_api_key),
):
    """
    Cancel a processing task
    """
    from waveq.exceptions import ResourceNotFoundError
    
    if task_id not in tasks_db:
        raise ResourceNotFoundError(f"Task not found: {task_id}")
    
    task = tasks_db[task_id]
    task.status = ProcessingStatus.CANCELLED
    
    return {"message": f"Task {task_id} cancelled"}
