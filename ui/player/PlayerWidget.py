import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject

class PlayerWidget(Gtk.Box):

    def __init__(self, name = "", score = 0):
        Gtk.Box.__init__(self)
        self.nameLabel = Gtk.Label(name)
        self.scoreLabel = Gtk.Label(score)

        self.add(self.nameLabel)
        self.add(Gtk.Label(": "))
        self.add(self.scoreLabel)

        self.show_all()

    def setName(self, name):
        self.nameLabel.set_text(name)

    def setScore(self, score):
        self.scoreLabel.set_text(score)