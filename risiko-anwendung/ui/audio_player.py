import gi

import os
from enum import Enum

_GST_AVAILABLE = False
try:
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst, GLib

    Gst.init(None)
    _GST_AVAILABLE = True
except (ImportError, ValueError):
    Gst = None
    GLib = None


def is_gst_available():
    return _GST_AVAILABLE


class PlayerState(Enum):
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"


class GstPlaybinPlayer:
    def __init__(self):
        if not _GST_AVAILABLE:
            raise RuntimeError("GStreamer (Gst) is not available")

        self._playbin = Gst.ElementFactory.make("playbin", None)
        if self._playbin is None:
            raise RuntimeError("Failed to create GStreamer 'playbin' element")

        self._bus = self._playbin.get_bus()
        self._bus_watch_installed = False
        self._bus_handler_id = None
        self._last_state = Gst.State.NULL
        self._on_state_changed = None

    def set_on_state_changed(self, callback):
        self._on_state_changed = callback

    def _emit_state(self, state):
        if self._on_state_changed is None:
            return

        try:
            self._on_state_changed(state)
        except Exception:
            # UI callbacks should not break the GStreamer bus handler.
            pass

    def play_file(self, path):
        uri = GLib.filename_to_uri(os.path.abspath(path), None)
        self._playbin.set_property("uri", uri)

        if not self._bus_watch_installed:
            self._bus.add_signal_watch()
            self._bus_handler_id = self._bus.connect("message", self._on_message)
            self._bus_watch_installed = True

        self._playbin.set_state(Gst.State.PLAYING)
        self._last_state = Gst.State.PLAYING
        self._emit_state(PlayerState.PLAYING)

    def pause(self):
        self._playbin.set_state(Gst.State.PAUSED)
        self._last_state = Gst.State.PAUSED
        self._emit_state(PlayerState.PAUSED)

    def resume(self):
        self._playbin.set_state(Gst.State.PLAYING)
        self._last_state = Gst.State.PLAYING
        self._emit_state(PlayerState.PLAYING)

    def get_state(self):
        # Non-blocking state query; falls back to last requested state.
        try:
            return self._playbin.get_state(0).state
        except Exception:
            return self._last_state

    def is_playing(self):
        return self.get_state() == Gst.State.PLAYING

    def is_paused(self):
        return self.get_state() == Gst.State.PAUSED

    def is_stopped(self):
        # We treat NULL as "stopped" (also used after EOS).
        return self.get_state() == Gst.State.NULL

    def stopMedia(self):
        self._playbin.set_state(Gst.State.NULL)
        self._last_state = Gst.State.NULL
        self._emit_state(PlayerState.STOPPED)

    def _on_message(self, bus, message):
        message_type = message.type
        if message_type == Gst.MessageType.EOS:
            self.stopMedia()
        elif message_type == Gst.MessageType.ERROR:
            self.stopMedia()
