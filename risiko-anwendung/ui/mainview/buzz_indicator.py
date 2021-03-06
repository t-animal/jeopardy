import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class BuzzIndicator(Gtk.Dialog):

    CORRECT = 0
    INCORRECT = 1
    OOPS = 2

    def __init__(self, player, parent):
        Gtk.Dialog.__init__(self)

        self.add_button("Oops", BuzzIndicator.OOPS)
        self.add_button("Correct", BuzzIndicator.CORRECT)
        self.add_button("Wrong!", BuzzIndicator.INCORRECT)

        self.get_content_area().add(Gtk.Label(player.name + " has buzzered"))

        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.show_all()

    def placeAtBottomRightOf(self, otherWindow):
        otherX, otherY = otherWindow.get_position()
        otherWidth, otherHeight = otherWindow.get_size()
        selfWidth, selfHeight = self.get_size()

        self.move(otherX + otherWidth - selfWidth - 50, otherY + otherHeight - selfHeight - 50)