import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango
from typing import Callable

from risiko_anwendung.model.game import NobodyKnewResult
from risiko_anwendung.model.types import AnswerValue, ResultByAnswer, ResultLike
from risiko_anwendung.ui.answers import AnswerBox
from risiko_anwendung.util import createSignal

SIG_ANSWER_SELECTED = "answerSelected"

class AnswerGrid(Gtk.Box):
    def __init__(self) -> None:
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
    
    def initComponents(self, rows: int = 5, cols: int = 5) -> None:
        self.headline = tuple([Gtk.Label(label="Headline " + str(i), name="headline") for i in range(1, cols + 1)])

        createSlot = lambda row, col: Slot(row, lambda: self._onSlotSelected(row, col))
        createRow = lambda row: tuple([createSlot(row, col) for col in range(0, cols)])
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

    def _onSlotSelected(self, row: int, col: int) -> None:
        self.emit(SIG_ANSWER_SELECTED, row, col)
    
    def focus(self) -> None:
        for row in self.slots:
            buttons = [slot._button for slot in filter(lambda x: x.hasButton(), row)]
            if len(buttons) == 0:
                continue

            buttons[0].set_can_focus(True)
            buttons[0].grab_focus()
            return

    @property
    def cols(self):
        return len(self.headline)

    @property
    def rows(self):
        return len(self.slots)

AnswerSelectedCallback = Callable[[], None]

class Slot(Gtk.Box):
    def __init__(self, row: int, onAnswerSelected: AnswerSelectedCallback | None = None):
        Gtk.Box.__init__(self)
        self._onAnswerSelected = onAnswerSelected
        self._row = row
        self.answer: AnswerBox | None = None # Is initialized by MainWindowInitializer

        self.results: ResultByAnswer = []
        self._button = self._createButton()
        self._label = Gtk.Label(label="", name="results-label")

        self.repack()

    def addResult(self, result: ResultLike) -> None:
        self.results.append(result)
        self.repack()
    
    def hasButton(self) -> bool:
        return bool(self._button.get_ancestor(Gtk.Box) == self)

    def repack(self) -> None:
        if self._button.get_ancestor(Gtk.Box) == self:
            self.remove(self._button)

        if self._label.get_ancestor(Gtk.Box) == self:
            self.remove(self._label)

        if len(self.results) == 0:
            self.pack_start(self._button, True, True, 0)
        else:
            self._label = Gtk.Label(label="", name="results-label")
            self._label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
            self._label.set_lines(2)
            if any(map(lambda r: r.correct, self.results)):
                winner = next(filter(lambda r: r.correct, self.results))
                if winner.player is not None:
                    winnerId = "player-" + str(winner.player.id)
                    self._label.get_style_context().add_class(winnerId)

            if any(map(lambda r: type(r) == NobodyKnewResult, self.results)):
                self._label.get_style_context().add_class("nobody-knew")

            if len(self.results) < 4:
                self._label.set_text("\n".join([result.getLabel() for result in self.results]))
            else:
                text = "\n".join([result.getLabel() for result in self.results[:2]])
                text += "\n...\n"
                text += self.results[-1].getLabel()
                self._label.set_text(text)

            self.pack_start(self._label, True, True, 0)

        self.show_all()
        self.queue_draw()

    def _handleButtonClicked(self, _target: Gtk.Button) -> None:
        if self._onAnswerSelected is not None:
            self._onAnswerSelected()

    def _createButton(self) -> Gtk.Button:
        self._button = Gtk.Button(label=str((self._row + 1) * 100))
        self._button.connect("clicked", self._handleButtonClicked)
        return self._button

createSignal(SIG_ANSWER_SELECTED, AnswerGrid, [int, int])
