import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, Pango

from risiko_anwendung.ui.audio_player import GstPlaybinPlayer, PlayerState, is_gst_available
from risiko_anwendung.model.game import SpecialField
from risiko_anwendung.model.types import AnswerValue, CategoryName
from risiko_anwendung.model.player import PlayerManager

class AnswerFactory:

    def __init__(self, playerManager: PlayerManager):
        self.playerManager = playerManager

    def createAnswer(self, category: CategoryName, answer: AnswerValue) -> "AnswerBox":
        if SpecialField.isSpecialField(answer):
            if SpecialField.IMAGE_ANSWER in answer.specialties:
                return ImageAnswer(self.playerManager, category, answer.scalar)

            if SpecialField.AUDIO_ANSWER in answer.specialties:
                return AudioAnswer(self.playerManager, category, answer.scalar)

            return TextAnswer(self.playerManager, category, str(answer))

        assert isinstance(answer, str)
        return TextAnswer(self.playerManager, category, answer)

class AnswerBox(Gtk.Box):

    def __init__(self, playerManager: PlayerManager, category: CategoryName):
        Gtk.Box.__init__(self)
        self.playerManager = playerManager

        self.set_orientation(Gtk.Orientation.VERTICAL)

        label = Gtk.Label(label=category, name="headline")
        self.pack_start(label, False, True, 0)

    def packed(self) -> None:
        pass

    def stopMedia(self) -> None:
        pass

    def toggleMedia(self) -> None:
        pass

class TextAnswer(AnswerBox):
    def __init__(self, playerManager: PlayerManager, category: CategoryName, text: str):
        super().__init__(playerManager, category)

        label = Gtk.Label(label=text)
        label.set_line_wrap(True)
        label.set_line_wrap_mode(wrap_mode=Pango.WrapMode.WORD_CHAR)

        # setting lines to 1 and ellipsize prevents a bug where alt-tabbing would cause inexplicable vertical growth of the window
        # the text will still wrap, but it won't cause the window to grow indefinitely when alt-tabbing
        label.set_lines(1)
        label.set_ellipsize(Pango.EllipsizeMode.END)

        self.pack_start(label, True, True, 0)

        self.show_all()

class ImageAnswer(AnswerBox):
    def __init__(self, playerManager: PlayerManager, category: CategoryName, imageUrl: str):
        super().__init__(playerManager, category)
        self.imageUrl = imageUrl

        pixbuf: GdkPixbuf.Pixbuf | GdkPixbuf.PixbufAnimation | None = None
        if imageUrl.endswith('gif'):
            pixbuf = GdkPixbuf.PixbufAnimation.new_from_file(self.imageUrl)
        else:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.imageUrl)

        if pixbuf is None:
            raise RuntimeError("Failed to load image from " + self.imageUrl)

        self.pixbuf = pixbuf
        self.image: Gtk.Image | None = None

    def packed(self) -> None:
        allocation = self.get_toplevel().get_allocation()
        imageWidth = self.pixbuf.get_width()
        imageHeight = self.pixbuf.get_height()

        desiredWidth = allocation.width * 0.8
        desiredHeight = imageHeight / imageWidth * desiredWidth

        if desiredHeight > allocation.height * 0.8:
            newDesiredHeight = allocation.height * 0.8
            desiredWidth = desiredWidth * newDesiredHeight / desiredHeight
            desiredHeight = newDesiredHeight

        if isinstance(self.pixbuf, GdkPixbuf.PixbufAnimation):
            newImage = Gtk.Image.new_from_animation(self.pixbuf)
        else:
            pixbuf = self.pixbuf.scale_simple(int(desiredWidth), int(desiredHeight), GdkPixbuf.InterpType.BILINEAR)
            newImage = Gtk.Image.new_from_pixbuf(pixbuf)

        if not self.image is None:
            self.remove(self.image)
        self.pack_start(newImage, True, True, 0)
        self.image = newImage

        self.show_all()

class AudioAnswer(AnswerBox):
    def __init__(self, playerManager: PlayerManager, category: CategoryName, audioPath: str):
        super().__init__(playerManager, category)

        self.audioPath = audioPath
        self._started = False

        title = Gtk.Label(label="Audio clue")
        self.pack_start(title, False, True, 0)

        self._statusLabel = Gtk.Label()
        self._statusLabel.set_halign(Gtk.Align.CENTER)
        self._statusLabel.set_justify(Gtk.Justification.CENTER)
        self._set_status("⏹")
        self.pack_start(self._statusLabel, False, True, 0)
        self._player: GstPlaybinPlayer | None = None

        if not is_gst_available():
            warning = Gtk.Label(label="GStreamer not available: cannot play audio")
            warning.set_line_wrap(True)
            warning.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
            warning.set_max_width_chars(40)
            self.pack_start(warning, False, True, 0)
        else:
            self._player = GstPlaybinPlayer()
            self._player.set_on_state_changed(self._on_player_state_changed)

        self.show_all()

    def _set_status(self, symbol: str) -> None:
        # Use markup to make the label large.
        self._statusLabel.set_markup(f'<span size="xx-large">{symbol}</span>')

    def _on_player_state_changed(self, state: PlayerState) -> None:
        if state == PlayerState.PLAYING:
            self._set_status("▶")
        elif state == PlayerState.PAUSED:
            self._set_status("⏸")
        elif state == PlayerState.STOPPED:
            self._set_status("⏹")
            # Treat STOPPED as "not started" for F7 restart semantics.
            self._started = False

    def packed(self) -> None:
        if self._started or self._player is None:
            return

        self._player.play_file(self.audioPath)
        self._started = True

    def toggleMedia(self) -> None:
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

    def stopMedia(self) -> None:
        if self._player is None:
            return

        self._player.stopMedia()
        self._started = False