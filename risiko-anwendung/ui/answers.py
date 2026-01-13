import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf

import os

from .audio_player import GstPlaybinPlayer, PlayerState, is_gst_available
from ..model.game import SpecialField

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

    def toggleMedia(self):
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

class AudioAnswer(Answer):
    def __init__(self, playerManager, category, audioPath):
        super().__init__(playerManager, category)

        self.audioPath = audioPath
        self._started = False

        title = Gtk.Label("Audio clue")
        self.pack_start(title, False, True, 0)

        self._statusLabel = Gtk.Label()
        self._statusLabel.set_halign(Gtk.Align.CENTER)
        self._statusLabel.set_justify(Gtk.Justification.CENTER)
        self._set_status("⏹")
        self.pack_start(self._statusLabel, False, True, 0)

        if not is_gst_available():
            warning = Gtk.Label("GStreamer not available: cannot play audio")
            warning.set_line_wrap(True)
            warning.set_line_wrap_mode(2)
            warning.set_max_width_chars(40)
            self.pack_start(warning, False, True, 0)

            self._player = None
        else:
            self._player = GstPlaybinPlayer()
            self._player.set_on_state_changed(self._on_player_state_changed)

        self.show_all()

    def _set_status(self, symbol):
        # Use markup to make the label large.
        self._statusLabel.set_markup(f'<span size="xx-large">{symbol}</span>')

    def _on_player_state_changed(self, state):
        if state == PlayerState.PLAYING:
            self._set_status("▶")
        elif state == PlayerState.PAUSED:
            self._set_status("⏸")
        elif state == PlayerState.STOPPED:
            self._set_status("⏹")
            # Treat STOPPED as "not started" for F7 restart semantics.
            self._started = False

    def packed(self):
        if self._started or self._player is None:
            return

        self._player.play_file(self.audioPath)
        self._started = True

    def toggleMedia(self):
        if self._player is None:
            return

        if (not self._started) or self._player.is_stopped():
            self._player.play_file(self.audioPath)
            self._started = True
            return

        if self._player.is_playing():
            self._player.pause()
        elif self._player.is_paused():
            self._player.resume()
        else:
            self._player.play_file(self.audioPath)
            self._started = True

    def stopMedia(self):
        if self._player is None:
            return

        self._player.stopMedia()
        self._started = False