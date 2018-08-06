import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject

class PlayerNameDialog(Gtk.Dialog):

    def __init__(self, parent, playerKey, playerName = ""):
        Gtk.Dialog.__init__(self, "Welcome, Player!", parent, 0)
        self.set_modal(True)

        label = Gtk.Label()
        label.set_markup("Your key will be:\n\n <b>" + playerKey + "</b>\n\n How do you want to be called?")
        self.nameEntry = Gtk.Entry()
        self.nameEntry.set_text(playerName)

        box = self.get_content_area()
        box.add(label)
        box.add(self.nameEntry)

        self.add_button("Whoopsie-daisy", Gtk.ResponseType.CANCEL)
        self.add_button("Letsa-go!", Gtk.ResponseType.OK)
        self.show_all()

        self.connect("key-release-event", self._onKeyRelease)

    def getName(self):
        return self.nameEntry.get_text()

    def _onKeyRelease(self, widget, event, data = None):
        if event.keyval == Gdk.KEY_Escape:
            self.response(Gtk.ResponseType.CANCEL)

        if event.keyval == Gdk.KEY_Return:
            self.response(Gtk.ResponseType.OK)