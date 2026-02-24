import gi

import os
from enum import Enum
from collections.abc import Callable
from typing import Any, TypeAlias

from gi.repository import GLib
_GST_AVAILABLE = False
try:
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst

    Gst.init([])
    _GST_AVAILABLE = True
except (ImportError, ValueError):
    # GStreamer is not available; audio features will be disabled.
    Gst = None # type: ignore


def is_gst_available():
    return _GST_AVAILABLE


class PlayerState(Enum):
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"


OnStateChangeCallback: TypeAlias = Callable[[PlayerState], None]

class GstPlaybinPlayer:
    def __init__(self) -> None:
        if Gst is None:
            raise RuntimeError("GStreamer (Gst) is not available")

        playbin = Gst.ElementFactory.make("playbin", None)
        if playbin is None:
            raise RuntimeError("Failed to create GStreamer 'playbin' element")

        bus = playbin.get_bus()
        if bus is None:
            raise RuntimeError("Failed to get GStreamer bus from playbin")
        
        self._gst = Gst # Store gst locally to prevent having to check for None everywhere

        self._bus = bus
        self._playbin = playbin
        self._bus_watch_installed = False
        self._bus_handler_id: int | None = None
        self._last_state = self._gst.State.NULL
        self._on_state_changed: OnStateChangeCallback | None = None

    def set_on_state_changed(self, callback: OnStateChangeCallback) -> None:
        self._on_state_changed = callback

    def _emit_state(self, state: PlayerState) -> None:
        if self._on_state_changed is None:
            return

        try:
            self._on_state_changed(state)
        except Exception:
            # UI callbacks should not break the GStreamer bus handler.
            pass

    def play_file(self, path: str) -> None:
        uri = GLib.filename_to_uri(os.path.abspath(path), None)
        self._playbin.set_property("uri", uri)

        if not self._bus_watch_installed:
            self._bus.add_signal_watch()
            self._bus_handler_id = self._bus.connect("message", self._on_message)
            self._bus_watch_installed = True

        self._playbin.set_state(self._gst.State.PLAYING)
        self._last_state = self._gst.State.PLAYING
        self._emit_state(PlayerState.PLAYING)

    def pause(self) -> None:
        self._playbin.set_state(self._gst.State.PAUSED)
        self._last_state = self._gst.State.PAUSED
        self._emit_state(PlayerState.PAUSED)

    def resume(self) -> None:
        self._playbin.set_state(self._gst.State.PLAYING)
        self._last_state = self._gst.State.PLAYING
        self._emit_state(PlayerState.PLAYING)

    def _get_state(self):
        # Non-blocking state query; falls back to last requested state.
        try:
            return self._playbin.get_state(0)[1]
        except Exception:
            return self._last_state

    def is_playing(self) -> bool:
        return bool(self._get_state() == self._gst.State.PLAYING)

    def is_paused(self) -> bool:
        return bool(self._get_state() == self._gst.State.PAUSED)

    def is_stopped(self) -> bool:
        # We treat NULL as "stopped" (also used after EOS).
        return bool(self._get_state() == self._gst.State.NULL)

    def stopMedia(self) -> None:
        self._playbin.set_state(self._gst.State.NULL)
        self._last_state = self._gst.State.NULL
        self._emit_state(PlayerState.STOPPED)

    def _on_message(self, bus: Any, message: Any) -> None:
        message_type = message.type
        if message_type == self._gst.MessageType.EOS:
            self.stopMedia()
        elif message_type == self._gst.MessageType.ERROR:
            self.stopMedia()
