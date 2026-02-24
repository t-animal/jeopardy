import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject

class PlayerWidget(Gtk.Box):

    def __init__(self, name: str = "", score: int = 0):
        Gtk.Box.__init__(self)
        self.nameLabel = Gtk.Label(label=name)
        self.scoreLabel = Gtk.Label(label=str(score))

        self.add(self.nameLabel)
        self.add(Gtk.Label(label=": "))
        self.add(self.scoreLabel)

        self.show_all()

    def setName(self, name: str) -> None:
        self.nameLabel.set_text(name)

    def setScore(self, score: int) -> None:
        self.scoreLabel.set_text(str(score))