import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class AnswerFactory:

    def __init__(self, playerManager):
        self.playerManager = playerManager

    def createAnswer(self, category, text):
        return TextAnswer(self.playerManager, category, text)

class Answer(Gtk.Box):

    def __init__(self, playerManager):
        Gtk.Box.__init__(self)
        self.playerManager = playerManager

class TextAnswer(Answer):
    def __init__(self, playerManager, category, text):
        super().__init__(playerManager)

        self.set_orientation(Gtk.Orientation.VERTICAL)

        self.pack_start(Gtk.Label(category), False, True, 0)
        self.pack_start(Gtk.Label(text), True, True, 0)

        self.show_all()