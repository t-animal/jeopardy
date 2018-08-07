import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class WagerPrompt(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, title="Double jeopardy!")

        self.wagerInput = Gtk.SpinButton(adjustment=Gtk.Adjustment(0, 100, 99999999, 100, 100, 100))

        self.get_content_area().add(Gtk.Label("How much do you want to wager?"))
        self.get_content_area().add(self.wagerInput)

        self.add_button("Ok", 0)

        self.set_transient_for(parent)
        self.set_modal(True)
        self.show_all()

        self.set_keep_above(True)