class VideoGenerationError(Exception):
    """Base exception for video generation errors"""
    pass

class LLMError(VideoGenerationError):
    """Exception for LLM-related failures"""
    pass

class TTSError(VideoGenerationError):
    """Exception for TTS-related failures"""
    pass