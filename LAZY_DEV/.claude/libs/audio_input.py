"""
Audio Input Module - Record audio from microphone

Supports:
- Continuous recording
- Event-based start/stop (for PTT mode)
- Multiple audio formats
"""

import pyaudio
import numpy as np
from threading import Thread
from typing import Optional, Callable
import time


class AudioRecorder:
    """Record audio from microphone with start/stop controls"""

    def __init__(
        self,
        sample_rate: int = 16000,
        chunk: int = 1024,
        channels: int = 1,
        format: int = pyaudio.paFloat32,
    ):
        """
        Initialize audio recorder

        Args:
            sample_rate: Sample rate in Hz (16000 for speech)
            chunk: Chunk size for audio buffer
            channels: Number of audio channels (1 for mono)
            format: Audio format (pyaudio.paFloat32 recommended)
        """
        self.sample_rate = sample_rate
        self.chunk = chunk
        self.channels = channels
        self.format = format

        self.frames = []
        self.is_recording = False
        self.thread: Optional[Thread] = None

        self.audio = pyaudio.PyAudio()
        self.stream = None

    def start_recording(self) -> None:
        """Start recording audio in background thread"""
        if self.is_recording:
            return

        self.is_recording = True
        self.frames = []

        self.thread = Thread(target=self._record_audio, daemon=True)
        self.thread.start()

    def stop_recording(self) -> bytes:
        """Stop recording and return audio bytes"""
        if not self.is_recording:
            return b""

        self.is_recording = False

        if self.thread:
            self.thread.join(timeout=2)

        return self._frames_to_bytes(self.frames)

    def get_recording_duration(self) -> float:
        """Get duration of current recording in seconds"""
        if not self.frames:
            return 0.0
        samples = len(self.frames) * self.chunk
        return samples / self.sample_rate

    def _record_audio(self) -> None:
        """Record audio continuously"""
        try:
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk,
            )

            while self.is_recording:
                try:
                    data = self.stream.read(self.chunk, exception_on_overflow=False)
                    self.frames.append(data)
                except Exception as e:
                    print(f"⚠️ Audio read error: {e}")
                    break

            if self.stream:
                self.stream.stop_stream()
                self.stream.close()

        except Exception as e:
            print(f"❌ Audio recording error: {e}")

    def _frames_to_bytes(self, frames: list) -> bytes:
        """Convert frame list to audio bytes"""
        return b"".join(frames)

    def cleanup(self) -> None:
        """Clean up audio resources"""
        self.is_recording = False
        if self.stream:
            try:
                self.stream.close()
            except:
                pass
        if self.audio:
            try:
                self.audio.terminate()
            except:
                pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.cleanup()


class AudioListenerContext:
    """Context manager for recording with callbacks"""

    def __init__(
        self,
        on_start: Optional[Callable] = None,
        on_stop: Optional[Callable] = None,
        sample_rate: int = 16000,
    ):
        self.on_start = on_start
        self.on_stop = on_stop
        self.recorder = AudioRecorder(sample_rate=sample_rate)

    def start(self) -> None:
        """Start recording"""
        self.recorder.start_recording()
        if self.on_start:
            self.on_start()

    def stop(self) -> bytes:
        """Stop recording and get audio"""
        audio = self.recorder.stop_recording()
        if self.on_stop:
            self.on_stop()
        return audio

    def cleanup(self) -> None:
        """Cleanup resources"""
        self.recorder.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.cleanup()
