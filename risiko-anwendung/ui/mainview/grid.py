import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from ..answers import TextAnswer

class AnswerGrid(Gtk.Grid):
    def __init__(self):
        Gtk.Grid.__init__(self)

        self.set_column_homogeneous(True)
        self.set_row_homogeneous(True)

        self.initComponents()
    
    def initComponents(self, rows = 5, cols = 5):
        self.headline = tuple([Gtk.Button(label="Headline " + str(i)) for i in range(1, rows + 1)])

        createRow = lambda row: tuple([Slot(col, row, None) for col in range(0, cols)]) #TODO: col row einheitlich
        self.slots = tuple([createRow(row) for row in range(0, rows)])

        for child in self.get_children():
            self.remove(child)

        for col in range(0, cols):
            self.attach(self.headline[col], col, 0, 1, 1)
            for row in range(0, rows):
                self.attach(self.slots[row][col], col, row + 1, 1, 1)

    @property
    def cols(self):
        return len(self.headline)

    @property
    def rows(self):
        return len(self.slots[0]) if len(self.slots) > 0 else 0

class Slot(Gtk.Box):
    def __init__(self, col, row, answer, doubleJeopardy=False): #TODO: double jeopardy aus nem model ziehen, nicht aus dem UI element
        Gtk.Box.__init__(self)
        self.col = col
        self.row = row
        self.answer = answer

        self.results = []
        self._button = self._createButton()
        self._label = Gtk.Label("")

        self.repack()

    def addResult(self, result):
        self.results.apend(result)
        self.repack()

    def repack(self):
        if self._button.get_ancestor(Gtk.Box) == self:
            self.remove(self._button)

        if len(self.results) == 0:
            self.pack_start(self._button, True, True, 0)
        else:
            if any(map(lambda r: type(r) == NobodyKnewResult, self.results)):
                self._label.get_style_context().add_class("nobody-knew")

            self._label.set_text("\n".join([result.getLabel() for result in self.results]))
            if self._label.get_ancestor(Gtk.Box) is None:
                self.pack_start(self._label, True, True, 0)
                self._label.show()

        self.show_all()
        self.queue_draw()

    def showAnswer(self, _target):
        self.get_toplevel().showAnswer(self.answer, self.row, self.col)

    def _createButton(self):
        self._button = Gtk.Button(label = (self.row + 1) * 100)
        self._button.connect("clicked", self.showAnswer)
        return self._button
