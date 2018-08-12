import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from ...model.game import NobodyKnewResult
from ..answers import TextAnswer

class AnswerGrid(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self)
        self.headlineGrid = Gtk.Grid(name="headlineGrid")
        self.answerGrid = Gtk.Grid(name="answerGrid")

        self.headlineGrid.set_column_homogeneous(True)
        self.answerGrid.set_column_homogeneous(True)
        self.answerGrid.set_row_homogeneous(True)

        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.pack_start(self.headlineGrid, False, False, 0)
        self.pack_start(self.answerGrid, True, True, 0)

        self.initComponents()
    
    def initComponents(self, rows = 5, cols = 5):
        self.headline = tuple([Gtk.Label("Headline " + str(i), name="headline") for i in range(1, rows + 1)])

        createRow = lambda row: tuple([Slot(col, row, None) for col in range(0, cols)]) #TODO: reihenfolge col row einheitlich
        self.slots = tuple([createRow(row) for row in range(0, rows)])

        for child in self.headlineGrid.get_children():
            self.headlineGrid.remove(child)
        for child in self.answerGrid.get_children():
            self.answerGrid.remove(child)

        for col in range(0, cols):
            self.headlineGrid.attach(self.headline[col], col, 0, 1, 1)
            for row in range(0, rows):
                self.answerGrid.attach(self.slots[row][col], col, row + 1, 1, 1)

        self.show_all()
    
    def focus(self):
        for row in self.slots:
            buttons = [slot._button for slot in filter(lambda x: x.hasButton(), row)]
            if len(buttons) == 0:
                continue
            print('grabbing')
            print(buttons[0])
            buttons[0].set_can_focus(True)
            buttons[0].grab_focus()
            return

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
        self._label = Gtk.Label("", name="results-label")

        self.repack()

    def addResult(self, result):
        self.results.append(result)
        self.repack()
    
    def hasButton(self):
        return self._button.get_ancestor(Gtk.Box) == self

    def repack(self):
        if self._button.get_ancestor(Gtk.Box) == self:
            self.remove(self._button)

        if self._label.get_ancestor(Gtk.Box) == self:
            self.remove(self._label)

        if len(self.results) == 0:
            self.pack_start(self._button, True, True, 0)
        else:
            self._label = Gtk.Label("", name="results-label")
            if any(map(lambda r: r.correct, self.results)):
                winnerId = "player-" + str(next(filter(lambda r: r.correct, self.results)).player.id)
                self._label.get_style_context().add_class(winnerId)

            if any(map(lambda r: type(r) == NobodyKnewResult, self.results)):
                self._label.get_style_context().add_class("nobody-knew")

            self._label.set_text("\n".join([result.getLabel() for result in self.results]))
            self.pack_start(self._label, True, True, 0)

        self.show_all()
        self.queue_draw()

    def showAnswer(self, _target):
        self.get_toplevel().showAnswer(self.answer, self.row, self.col)

    def _createButton(self):
        self._button = Gtk.Button(label = (self.row + 1) * 100)
        self._button.connect("clicked", self.showAnswer)
        return self._button
