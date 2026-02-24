import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from typing import Any

from risiko_anwendung.ui.mainview.grid import AnswerGrid, SIG_ANSWER_SELECTED
from risiko_anwendung.ui.mainview.buzz_indicator import BuzzIndicator
from risiko_anwendung.ui.mainview.wager_prompt import WagerPrompt

from risiko_anwendung.ui.player import PlayerWidget
from risiko_anwendung.ui.answers import AnswerBox, AnswerFactory
from risiko_anwendung.ui.rng import RngWindow

from risiko_anwendung.model import SIG_PLAYER_MODEL_CHANGED, SIG_GAME_MODEL_CHANGED
from risiko_anwendung.model.game import GameStateModel
from risiko_anwendung.model.game.history import HistoryRestorer
from risiko_anwendung.model.player import PlayerManager
from risiko_anwendung.model.types import AnswerValue, CategoryName
from risiko_anwendung.util import clearChildren

class MainWindow(Gtk.Window):

    def __init__(self, playerManager: PlayerManager, gameStateModel: GameStateModel, history: HistoryRestorer):
        Gtk.Window.__init__(self, title="Jeopardy")
        self.buzzIndicator: BuzzIndicator | None = None
        self.buzzerSignalId: int | None = None
        self._activeAnswer: AnswerBox | None = None

        self.playerManager = playerManager
        self.gameStateModel = gameStateModel
        self.history = history

        self.mainContainer = Gtk.Box()

        self.gridContainer = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.grid = AnswerGrid()
        self.grid.connect(SIG_ANSWER_SELECTED, self._onAnswerSelected)
        self.playerNamesBox = Gtk.Box(name="playerNamesBox")

        self.gridContainer.pack_start(self.grid, True, True, 0)
        self.gridContainer.pack_end(self.playerNamesBox, False, False, 0)

        self.mainContainer.pack_start(self.gridContainer, True, True, 0)
        self.add(self.mainContainer)

        self.connect("key-release-event", self._keyReleaseEvent)

    def _onAnswerSelected(self, _grid: AnswerGrid, row: int, col: int) -> None:
        answer = self.grid.slots[row][col].answer
        if answer is None:
            return

        self.showAnswer(answer, row, col)

    def showGrid(self) -> None:
        for child in self.mainContainer.get_children():
            if child == self.gridContainer:
                continue

            if isinstance(child, AnswerBox):
                child.stopMedia()

            self.mainContainer.remove(child)

        self._activeAnswer = None

        if not self.buzzerSignalId is None:
            self.disconnect(self.buzzerSignalId)
            self.buzzerSignalId = None

        self.gridContainer.show()

        self.grid.focus()

    def showAnswer(self, answer: AnswerBox, row: int, col: int) -> None:
        category = list(self.gameStateModel.getCategoryNames())[col]

        wager = (row + 1) * 100
        if self.gameStateModel.isDoubleJeopardy(category, row):
            wagerPrompt = WagerPrompt(self)
            wagerPrompt.run()
            wager = int(wagerPrompt.wagerInput.get_value())
            wagerPrompt.destroy()

        self.gridContainer.hide()

        self.mainContainer.pack_start(answer, True, True, 0)
        self._activeAnswer = answer
        self.buzzerSignalId = self.connect("key-release-event", self.buzzered, row, col, wager)
        answer.show()
        answer.packed()

    def buzzered(self, widget: Gtk.Widget, event: Gdk.EventKey, row: int, col: int, wager: int = 0) -> None:
        if event.keyval == Gdk.KEY_F7:
            if self._activeAnswer is not None:
                self._activeAnswer.toggleMedia()
            return

        if event.keyval == Gdk.KEY_Escape:
            if not self.buzzIndicator is None:
                self.buzzIndicator.destroy()
                self.buzzIndicator = None
                return
            
            self.showGrid()
            return
        
        if event.keyval == Gdk.KEY_F8:
            category = list(self.gameStateModel.getCategoryNames())[col]
            self.gameStateModel.setNobodyKnew(category, row)
            self.showGrid()
            return

        if self.playerManager.isPlayerKeyval(event.keyval) and self.buzzIndicator is None:
            activePlayer = self.playerManager.getPlayerByKeyval(event.keyval)
            self.buzzIndicator = BuzzIndicator(activePlayer, self)
            self.buzzIndicator.placeAtBottomRightOf(self)

            indicated = self.buzzIndicator.run()

            self.buzzIndicator.destroy()
            self.buzzIndicator = None

            if indicated == BuzzIndicator.INCORRECT:
                category = list(self.gameStateModel.getCategoryNames())[col]
                self.gameStateModel.addResult(category, row, activePlayer, False, wager)

            if indicated == BuzzIndicator.CORRECT:
                category = list(self.gameStateModel.getCategoryNames())[col]
                self.gameStateModel.addResult(category, row, activePlayer, True, wager)
                self.showGrid()
    

    def _keyReleaseEvent(self, widget: Gtk.Widget, event: Gdk.EventKey) -> None:
        if event.keyval == Gdk.KEY_F12:
            playerCount = len(self.playerManager.getPlayers())
            rng = RngWindow(upperLimit = playerCount + 1, duration=500, playerCount=playerCount)
            rng.present()
            rng.random()

        if event.keyval == Gdk.KEY_F9:
            self.history.undo()

        if event.keyval == Gdk.KEY_F10:
            self.history.redo()

class MainWindowInitializer():

    def __init__(self, playerManager: PlayerManager, gameStateModel: GameStateModel, mainWindow: MainWindow):
        self.answerFactory = AnswerFactory(playerManager)
        self.playerManager = playerManager
        self.gameStateModel = gameStateModel
        self._mainWindow = mainWindow
        self._grid = mainWindow.grid

        playerManager.connect(SIG_PLAYER_MODEL_CHANGED, self.initPlayers)
        gameStateModel.connect(SIG_GAME_MODEL_CHANGED, self.initGrid)
        gameStateModel.connect(SIG_GAME_MODEL_CHANGED, self.initPlayers)

    def initMainWindow(self) -> None:
        self.initPlayers()
        self.initGrid()

    def initPlayers(self, *event_args: object) -> None:
        clearChildren(self._mainWindow.playerNamesBox)

        for player in self.playerManager.getPlayers():
            points = self.gameStateModel.getPointsOfPlayer(player)
            widget = PlayerWidget(player.name, points)
            widget.get_style_context().add_class("player-" + str(player.id))
            self._mainWindow.playerNamesBox.pack_start(widget, False, False, 0)

    def initGrid(self, *event_args: object) -> None:
        cols = len(self.gameStateModel.getCategoryNames())

        for col, category in enumerate(self.gameStateModel.getCategoryNames()):
            answers = self.gameStateModel.getAnswers(category)

            if not self._grid.rows == len(answers) or not self._grid.cols == cols:
                self._grid.initComponents(len(answers), cols)

            self._grid.headline[col].set_text(category)
            for row, answer in enumerate(self.gameStateModel.getAnswers(category)):
                slot = self._grid.slots[row][col]
                slot.answer = self.answerFactory.createAnswer(category, answer)
                slot.results = self.gameStateModel.getResults(category, row)
                slot.repack()

