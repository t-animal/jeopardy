import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def createAnswer(category, text):
	return TextAnswer(category, text)

class TextAnswer(Gtk.Box):
	def __init__(self, category, text):
		Gtk.Box.__init__(self)
		self.set_orientation(Gtk.Orientation.VERTICAL)

		self.pack_start(Gtk.Label(category), False, True, 0)
		self.pack_start(Gtk.Label(text), True, True, 0)

		self.show_all()