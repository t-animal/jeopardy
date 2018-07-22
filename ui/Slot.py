import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Slot(Gtk.Box):
    def __init__(self, amount, answer, doubleJeopardy=False):
        Gtk.Box.__init__(self)
        self.amount = amount
        self.answer = answer

        self.results = []
        self._button = self._createButton()
        self._label = Gtk.Label("")

        self.repack()

    def repack(self):
        if self._button.get_ancestor(Gtk.Box) == self:
            self.remove(self._button)

        if len(self.results) == 0:
            self.pack_start(self._button, True, True, 0)
        else:
            self._label.set_text("\n".join(self.results))
            self.pack_start(self._label, True, True, 0)
            self._label.show()

        self.queue_draw()

    def showAnswer(self, _target):
        #TODO: Show answer window
        self.repack()

    def _createButton(self):
        self._button = Gtk.Button(label = self.amount)
        self._button.connect("clicked", self.showAnswer)
        return self._button