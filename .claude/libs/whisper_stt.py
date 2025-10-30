"""
Speech-To-Text Module - Transcribe audio using OpenAI Whisper API

Supports:
- Audio file transcription (.wav, .mp3, .m4a, etc.)
- Raw audio bytes transcription
- Multiple languages
- Language auto-detection
"""

import openai
import io
from pathlib import Path
from typing import Optional


class WhisperSTT:
    """Transcribe audio using OpenAI Whisper API"""

    # Supported audio formats
    SUPPORTED_FORMATS = ["mp3", "mp4", "mpeg", "mpga", "m4a", "ogg", "opus", "flac", "wav"]

    def __init__(self, api_key: str, model: str = "whisper-1", org_id: Optional[str] = None):
        """
        Initialize Whisper STT client

        Args:
            api_key: OpenAI API key
            model: Whisper model to use (default: whisper-1)
            org_id: Optional OpenAI organization ID
        """
        self.api_key = api_key
        self.model = model

        # Configure OpenAI client
        openai.api_key = api_key
        if org_id:
            openai.organization = org_id

    def transcribe_audio(
        self, audio_bytes: bytes, language: str = "en", file_extension: str = "wav"
    ) -> str:
        """
        Transcribe audio bytes using Whisper API

        Args:
            audio_bytes: Raw audio bytes
            language: Language code (e.g., "en", "fr", "es")
            file_extension: File extension for audio format

        Returns:
            Transcribed text

        Raises:
            ValueError: If API call fails
        """
        try:
            # Create file-like object
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = f"audio.{file_extension}"

            # Call Whisper API
            transcript = openai.Audio.transcribe(
                model=self.model,
                file=audio_file,
                language=language,
            )

            return transcript.get("text", "").strip()

        except openai.error.OpenAIError as e:
            raise ValueError(f"Whisper API error: {e}")

    def transcribe_file(
        self, file_path: str, language: Optional[str] = None
    ) -> str:
        """
        Transcribe audio file

        Args:
            file_path: Path to audio file
            language: Language code (optional, auto-detect if None)

        Returns:
            Transcribed text

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format not supported
        """
        path = Path(file_path)

        # Validate file exists
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        # Validate file format
        file_ext = path.suffix.lstrip(".").lower()
        if file_ext not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported audio format: {file_ext}. Supported: {', '.join(self.SUPPORTED_FORMATS)}")

        # Read file
        with open(file_path, "rb") as f:
            audio_bytes = f.read()

        # Transcribe
        kwargs = {
            "audio_bytes": audio_bytes,
            "file_extension": file_ext,
        }

        if language:
            kwargs["language"] = language

        return self.transcribe_audio(**kwargs)

    def transcribe_with_context(
        self, audio_bytes: bytes, context_prompt: str = "", language: str = "en"
    ) -> str:
        """
        Transcribe with optional context prompt for better results

        Args:
            audio_bytes: Raw audio bytes
            context_prompt: Optional context to help with transcription
                           (e.g., "REST API, OAuth2, authentication")
            language: Language code

        Returns:
            Transcribed text
        """
        # Note: Whisper API doesn't directly support context prompts,
        # but we can use them for post-processing hints
        try:
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.wav"

            # Call API with prompt parameter (if supported)
            transcript = openai.Audio.transcribe(
                model=self.model,
                file=audio_file,
                language=language,
                prompt=context_prompt,  # Helps with technical terms
            )

            return transcript.get("text", "").strip()

        except TypeError:
            # If prompt not supported, just transcribe normally
            return self.transcribe_audio(audio_bytes, language)

    def detect_language(self, audio_bytes: bytes) -> str:
        """
        Detect language of audio

        Args:
            audio_bytes: Raw audio bytes

        Returns:
            Language code (e.g., "en", "fr", "es")
        """
        try:
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.wav"

            # Call Whisper API to detect language
            result = openai.Audio.transcribe(
                model=self.model,
                file=audio_file,
            )

            # The API includes detected language info
            return result.get("language", "en")

        except Exception:
            return "en"  # Default to English

    @staticmethod
    def is_valid_format(file_path: str) -> bool:
        """Check if file format is supported"""
        path = Path(file_path)
        ext = path.suffix.lstrip(".").lower()
        return ext in WhisperSTT.SUPPORTED_FORMATS

    @staticmethod
    def list_supported_formats() -> list:
        """Get list of supported audio formats"""
        return WhisperSTT.SUPPORTED_FORMATS.copy()
