import logging
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class FullscreenManager:

    def __init__(self, monitorNumber: int = 1, keyval: int = Gdk.KEY_F11):
        self.monitorNumber = monitorNumber
        self.keyval = keyval
        self.fullscreenEnabled = False
        self.windows: list[Gtk.Window] = []
        self.positionBeforeFullscreen: dict[Gtk.Window, tuple[int, int]] = {}

    def handleWindow(self, window: Gtk.Window) -> None:
        window.connect("key-release-event", self._onKeyRelease)
        self._applyStateToWindow(window, self.fullscreenEnabled)
        self.windows.append(window)

    def toggleAll(self) -> None:
        self.fullscreenEnabled = not self.fullscreenEnabled
        for window in self.windows:
            self._applyStateToWindow(window, self.fullscreenEnabled)

    def _onKeyRelease(self, widget: Gtk.Widget, event: Gdk.EventKey, data: object | None = None) -> None:
        if event.keyval == self.keyval:
            self.toggleAll()

    def _applyStateToWindow(self, window: Gtk.Window, enableFullscreen: bool) -> None:
        if enableFullscreen:
            screen = Gdk.Screen.get_default()
            if screen is None:
                logging.warning("Could not get default screen for fullscreen management; fullscreen will not work")
                return
            if screen.get_n_monitors() > 1:
                self.positionBeforeFullscreen[window] = window.get_position()
                window.fullscreen_on_monitor(window.get_screen(), 1)
            else:
                window.fullscreen()
            window.set_keep_above(True)
        else:
            window.unfullscreen()
            window.set_keep_above(False)
            if window in self.positionBeforeFullscreen:
                window.move(*self.positionBeforeFullscreen[window])