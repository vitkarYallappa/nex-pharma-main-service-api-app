"""
Storage configuration utilities.
Provides helper functions for storage operations.
"""
import os
import mimetypes
from typing import Optional, Tuple
from datetime import datetime


def get_content_type(filename: str) -> str:
    """
    Get content type from filename.
    
    Args:
        filename: Name of the file
        
    Returns:
        MIME content type
    """
    content_type, _ = mimetypes.guess_type(filename)
    return content_type or "application/octet-stream"


def generate_unique_filename(original_filename: str, prefix: str = "") -> str:
    """
    Generate a unique filename with timestamp.
    
    Args:
        original_filename: Original filename
        prefix: Optional prefix for the filename
        
    Returns:
        Unique filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(original_filename)
    
    if prefix:
        return f"{prefix}_{timestamp}_{name}{ext}"
    else:
        return f"{timestamp}_{name}{ext}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
    
    return filename


def get_file_size_mb(file_size_bytes: int) -> float:
    """
    Convert file size from bytes to megabytes.
    
    Args:
        file_size_bytes: File size in bytes
        
    Returns:
        File size in megabytes
    """
    return file_size_bytes / (1024 * 1024)


def validate_file_size(file_size_bytes: int, max_size_mb: float = 10.0) -> Tuple[bool, Optional[str]]:
    """
    Validate file size against maximum allowed size.
    
    Args:
        file_size_bytes: File size in bytes
        max_size_mb: Maximum allowed size in megabytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if file_size_bytes <= 0:
        return False, "File is empty"
    
    file_size_mb = get_file_size_mb(file_size_bytes)
    if file_size_mb > max_size_mb:
        return False, f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb} MB)"
    
    return True, None


def validate_file_extension(filename: str, allowed_extensions: list) -> Tuple[bool, Optional[str]]:
    """
    Validate file extension against allowed extensions.
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions (e.g., ['.jpg', '.png'])
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not filename:
        return False, "Filename is empty"
    
    _, ext = os.path.splitext(filename.lower())
    
    if not ext:
        return False, "File has no extension"
    
    if ext not in [e.lower() for e in allowed_extensions]:
        return False, f"File extension '{ext}' not allowed. Allowed extensions: {', '.join(allowed_extensions)}"
    
    return True, None


def get_storage_path(category: str, filename: str) -> str:
    """
    Generate storage path for a file based on category and date.
    
    Args:
        category: File category (e.g., 'documents', 'images')
        filename: Name of the file
        
    Returns:
        Storage path
    """
    date_path = datetime.now().strftime("%Y/%m/%d")
    return f"{category}/{date_path}/{filename}"


# Common file type configurations
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
DOCUMENT_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt', '.rtf']
ARCHIVE_EXTENSIONS = ['.zip', '.rar', '.7z', '.tar', '.gz']

# File size limits (in MB)
DEFAULT_MAX_FILE_SIZE = 10.0
IMAGE_MAX_FILE_SIZE = 5.0
DOCUMENT_MAX_FILE_SIZE = 20.0 