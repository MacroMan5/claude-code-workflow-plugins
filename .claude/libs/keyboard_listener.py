"""
Keyboard Listener Module - Detect push-to-talk key presses

Supports:
- Spacebar push-to-talk
- Custom key bindings
- Cross-platform (Windows, Mac, Linux)
"""

from pynput import keyboard
from typing import Optional, Callable
import threading
import time


class PushToTalkListener:
    """Listen for push-to-talk key presses (default: spacebar)"""

    def __init__(
        self,
        key_to_listen=keyboard.Key.space,
        on_press_callback: Optional[Callable] = None,
        on_release_callback: Optional[Callable] = None,
    ):
        """
        Initialize push-to-talk listener

        Args:
            key_to_listen: Key to listen for (default: spacebar)
            on_press_callback: Function to call when key is pressed
            on_release_callback: Function to call when key is released
        """
        self.key_to_listen = key_to_listen
        self.on_press = on_press_callback
        self.on_release = on_release_callback

        self.listener = None
        self.is_listening = False
        self.is_pressed = False

    def start(self) -> None:
        """Start listening for key presses"""
        if self.is_listening:
            return

        self.is_listening = True

        try:
            self.listener = keyboard.Listener(
                on_press=self._on_key_press, on_release=self._on_key_release
            )
            self.listener.start()
        except Exception as e:
            print(f"❌ Failed to start keyboard listener: {e}")
            self.is_listening = False

    def stop(self) -> None:
        """Stop listening for key presses"""
        if not self.is_listening:
            return

        self.is_listening = False

        if self.listener:
            try:
                self.listener.stop()
            except:
                pass

    def is_key_pressed(self) -> bool:
        """Check if PTT key is currently pressed"""
        return self.is_pressed

    def _on_key_press(self, key) -> None:
        """Handle key press event"""
        try:
            if key == self.key_to_listen:
                self.is_pressed = True
                if self.on_press:
                    self.on_press()
        except AttributeError:
            pass

    def _on_key_release(self, key) -> None:
        """Handle key release event"""
        try:
            if key == self.key_to_listen:
                self.is_pressed = False
                if self.on_release:
                    self.on_release()
        except AttributeError:
            pass

    def wait_for_press(self, timeout: float = None) -> bool:
        """
        Wait for key to be pressed

        Args:
            timeout: Maximum time to wait (seconds)

        Returns:
            True if key was pressed, False if timeout
        """
        start = time.time()
        while not self.is_pressed:
            if timeout and (time.time() - start) > timeout:
                return False
            time.sleep(0.01)
        return True

    def wait_for_release(self, timeout: float = None) -> bool:
        """
        Wait for key to be released (must be pressed first)

        Args:
            timeout: Maximum time to wait (seconds)

        Returns:
            True if key was released, False if timeout
        """
        start = time.time()
        while self.is_pressed:
            if timeout and (time.time() - start) > timeout:
                return False
            time.sleep(0.01)
        return True

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()


class KeyboardShortcutManager:
    """Manage multiple keyboard shortcuts"""

    def __init__(self):
        self.shortcuts = {}
        self.listener = None
        self.is_listening = False

    def register(
        self,
        key: keyboard.Key,
        callback: Callable,
        description: str = "",
    ) -> None:
        """
        Register a keyboard shortcut

        Args:
            key: Key to listen for
            callback: Function to call when key pressed
            description: Human-readable description
        """
        self.shortcuts[key] = {
            "callback": callback,
            "description": description,
        }

    def start(self) -> None:
        """Start listening for registered shortcuts"""
        if self.is_listening:
            return

        self.is_listening = True

        try:
            self.listener = keyboard.Listener(on_press=self._on_key_press)
            self.listener.start()
        except Exception as e:
            print(f"❌ Failed to start keyboard shortcuts: {e}")
            self.is_listening = False

    def stop(self) -> None:
        """Stop listening for shortcuts"""
        if not self.is_listening:
            return

        self.is_listening = False

        if self.listener:
            try:
                self.listener.stop()
            except:
                pass

    def _on_key_press(self, key) -> None:
        """Handle key press for registered shortcuts"""
        try:
            if key in self.shortcuts:
                callback = self.shortcuts[key]["callback"]
                # Run callback in thread to avoid blocking listener
                threading.Thread(target=callback, daemon=True).start()
        except:
            pass

    def list_shortcuts(self) -> None:
        """Print registered shortcuts"""
        print("📋 Registered Keyboard Shortcuts:")
        for key, info in self.shortcuts.items():
            print(f"   {key}: {info['description']}")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
