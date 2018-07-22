import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class AnswerFactory:

    def __init__(self, playerManager):
        self.playerManager = playerManager

    def createAnswer(self, category, text):
        return TextAnswer(self.playerManager, category, text)

class TextAnswer(Gtk.Box):
    def __init__(self, playerManager, category, text):
        Gtk.Box.__init__(self)
        self.playerManager = playerManager

        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.pack_start(Gtk.Label(category), False, True, 0)
        self.pack_start(Gtk.Label(text), True, True, 0)

        self.show_all()

        self.connect("key-release-event", self._onKeyRelease)

    def _onKeyRelease(self, widget, event, data = None):
        if playerManager.isPlayerKeycode(event.keyval):
            print("Player " + playerManager.getPlayerByKeycode(event.keyval) + " is on!")