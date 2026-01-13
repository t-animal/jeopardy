import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf

import os

from ..model.game import SpecialField

_GST_AVAILABLE = False
try:
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst, GLib

    Gst.init(None)
    _GST_AVAILABLE = True
except (ImportError, ValueError):
    Gst = None
    GLib = None

class AnswerFactory:

    def __init__(self, playerManager):
        self.playerManager = playerManager

    def createAnswer(self, category, answer):
        if SpecialField.isSpecialField(answer) and SpecialField.IMAGE_ANSWER in answer.specialties:
            return ImageAnswer(self.playerManager, category, answer.scalar)

        if SpecialField.isSpecialField(answer) and SpecialField.AUDIO_ANSWER in answer.specialties:
            return AudioAnswer(self.playerManager, category, answer.scalar)

        return TextAnswer(self.playerManager, category, answer)

class Answer(Gtk.Box):

    def __init__(self, playerManager, category):
        Gtk.Box.__init__(self)
        self.playerManager = playerManager

        self.set_orientation(Gtk.Orientation.VERTICAL)
        
        label = Gtk.Label(category, name="headline") 
        self.pack_start(label, False, True, 0)
    
    def packed(self):
        pass

    def stopMedia(self):
        pass

class TextAnswer(Answer):
    def __init__(self, playerManager, category, text):
        super().__init__(playerManager, category)

        label = Gtk.Label(text)
        label.set_line_wrap(True)
        label.set_line_wrap_mode(2)
        label.set_max_width_chars(20)
        self.pack_start(label, True, True, 0)

        self.show_all()

class ImageAnswer(Answer):
    def __init__(self, playerManager, category, imageUrl):
        super().__init__(playerManager, category)
        self.imageUrl = imageUrl
        if imageUrl.endswith('gif'):
            self.pixbuf = GdkPixbuf.PixbufAnimation.new_from_file(self.imageUrl)
        else:
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.imageUrl)
        self.image = None

    def packed(self):
        allocation = self.get_toplevel().get_allocation()
        imageWidth = self.pixbuf.get_width()
        imageHeight = self.pixbuf.get_height()

        desiredWidth = allocation.width * 0.8
        desiredHeight = imageHeight / imageWidth * desiredWidth

        if desiredHeight > allocation.height * 0.8:
            newDesiredHeight = allocation.height * 0.8
            desiredWidth = desiredWidth * newDesiredHeight / desiredHeight
            desiredHeight = newDesiredHeight

        if self.imageUrl.endswith('gif'):
            newImage = Gtk.Image.new_from_animation(self.pixbuf)
        else:
            pixbuf = self.pixbuf.scale_simple(desiredWidth, desiredHeight, GdkPixbuf.InterpType.BILINEAR)
            newImage = Gtk.Image.new_from_pixbuf(pixbuf)

        if not self.image is None:
            self.remove(self.image)
        self.pack_start(newImage, True, True, 0)
        self.image = newImage

        self.show_all()


class _GstPlaybinPlayer:
    def __init__(self):
        if not _GST_AVAILABLE:
            raise RuntimeError("GStreamer (Gst) is not available")

        self._playbin = Gst.ElementFactory.make("playbin", None)
        if self._playbin is None:
            raise RuntimeError("Failed to create GStreamer 'playbin' element")

        self._bus = self._playbin.get_bus()
        self._bus_watch_installed = False
        self._bus_handler_id = None

    def play_file(self, path):
        uri = GLib.filename_to_uri(os.path.abspath(path), None)
        self._playbin.set_property("uri", uri)

        if not self._bus_watch_installed:
            self._bus.add_signal_watch()
            self._bus_handler_id = self._bus.connect("message", self._on_message)
            self._bus_watch_installed = True

        self._playbin.set_state(Gst.State.PLAYING)

    def stopMedia(self):
        self._playbin.set_state(Gst.State.NULL)

    def _on_message(self, bus, message):
        message_type = message.type
        if message_type == Gst.MessageType.EOS:
            self.stopMedia()
        elif message_type == Gst.MessageType.ERROR:
            self.stopMedia()


class AudioAnswer(Answer):
    def __init__(self, playerManager, category, audioPath):
        super().__init__(playerManager, category)

        self.audioPath = audioPath
        self._player = None
        self._started = False

        title = Gtk.Label("Audio clue")
        self.pack_start(title, False, True, 0)

        filename = os.path.basename(audioPath)
        label = Gtk.Label(filename)
        label.set_line_wrap(True)
        label.set_line_wrap_mode(2)
        label.set_max_width_chars(30)
        self.pack_start(label, True, True, 0)

        if not _GST_AVAILABLE:
            warning = Gtk.Label("GStreamer not available: cannot play audio")
            warning.set_line_wrap(True)
            warning.set_line_wrap_mode(2)
            warning.set_max_width_chars(40)
            self.pack_start(warning, False, True, 0)

        self.show_all()

    def packed(self):
        if self._started or not _GST_AVAILABLE:
            return

        if self._player is None:
            self._player = _GstPlaybinPlayer()

        self._player.play_file(self.audioPath)
        self._started = True

    def stopMedia(self):
        if self._player is None:
            return

        self._player.stopMedia()
        self._started = False