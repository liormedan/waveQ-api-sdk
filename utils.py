"""
Utility functions for WaveQ
"""

import hashlib
import uuid
from pathlib import Path
from typing import Union, BinaryIO
import mimetypes


def generate_task_id() -> str:
    """Generate a unique task ID"""
    return f"task_{uuid.uuid4().hex[:16]}"


def generate_api_key() -> str:
    """Generate a new API key"""
    return f"waveq_{uuid.uuid4().hex}"


def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == hashed


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix.lower()


def get_mime_type(filename: str) -> str:
    """Get MIME type from filename"""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"


def is_audio_file(filename: str) -> bool:
    """Check if file is an audio file based on extension"""
    from config import settings
    ext = get_file_extension(filename)
    return ext in settings.ALLOWED_AUDIO_FORMATS


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal"""
    # Remove path components
    filename = Path(filename).name
    # Remove potentially dangerous characters
    filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
    return filename.strip()


def save_upload_file(file: BinaryIO, filename: str, upload_dir: Path) -> Path:
    """Save an uploaded file to disk"""
    safe_filename = sanitize_filename(filename)
    unique_filename = f"{uuid.uuid4().hex[:8]}_{safe_filename}"
    file_path = upload_dir / unique_filename
    
    with open(file_path, 'wb') as f:
        content = file.read()
        f.write(content)
    
    return file_path


async def async_save_upload_file(file: BinaryIO, filename: str, upload_dir: Path) -> Path:
    """Async version of save_upload_file"""
    import aiofiles
    
    safe_filename = sanitize_filename(filename)
    unique_filename = f"{uuid.uuid4().hex[:8]}_{safe_filename}"
    file_path = upload_dir / unique_filename
    
    content = await file.read()
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    return file_path


def estimate_processing_time(file_size_mb: float, operation: str) -> float:
    """Estimate processing time in seconds based on file size and operation"""
    # Rough estimates (in seconds per MB)
    estimates = {
        "denoise": 2.0,
        "transcribe": 3.0,
        "trim": 1.0,
        "separate": 5.0,
        "sentiment": 3.5,
        "tts": 0.5,
    }
    
    rate = estimates.get(operation, 2.0)
    return file_size_mb * rate
