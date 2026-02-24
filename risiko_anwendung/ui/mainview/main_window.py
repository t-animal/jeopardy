import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from risiko_anwendung.ui.mainview.grid import AnswerGrid, SIG_ANSWER_SELECTED
from risiko_anwendung.ui.mainview.buzz_indicator import BuzzIndicator
from risiko_anwendung.ui.mainview.wager_prompt import WagerPrompt

from risiko_anwendung.ui.player import PlayerWidget
from risiko_anwendung.ui.answers import AnswerBox, AnswerFactory
from risiko_anwendung.ui.console_output import clear_current_question_box, print_current_question
from risiko_anwendung.ui.rng import RngWindow

from risiko_anwendung.model import SIG_PLAYER_MODEL_CHANGED, SIG_GAME_MODEL_CHANGED
from risiko_anwendung.model.game import GameStateModel
from risiko_anwendung.model.game.history import HistoryRestorer
from risiko_anwendung.model.player import PlayerManager
from risiko_anwendung.model.types import ResultByAnswer
from risiko_anwendung.util import clearChildren

class MainWindow(Gtk.Window):

    def __init__(self, playerManager: PlayerManager, gameStateModel: GameStateModel, history: HistoryRestorer, answerFactory: AnswerFactory):
        Gtk.Window.__init__(self, title="Jeopardy")
        self.buzzIndicator: BuzzIndicator | None = None
        self.buzzerSignalId: int | None = None
        self._activeAnswer: AnswerBox | None = None

        self.playerManager = playerManager
        self.gameStateModel = gameStateModel
        self.history = history
        self.answerFactory = answerFactory

        self.mainContainer = Gtk.Box()

        self.gridContainer = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.grid = AnswerGrid(gameStateModel)
        self.grid.connect(SIG_ANSWER_SELECTED, self._onAnswerSelected)
        self.playerNamesBox = Gtk.Box(name="playerNamesBox")

        self.gridContainer.pack_start(self.grid, True, True, 0)
        self.gridContainer.pack_end(self.playerNamesBox, False, False, 0)

        self.mainContainer.pack_start(self.gridContainer, True, True, 0)
        self.add(self.mainContainer)

        playerManager.connect(SIG_PLAYER_MODEL_CHANGED, self._initPlayers)
        gameStateModel.connect(SIG_GAME_MODEL_CHANGED, self._initPlayers)

        self.connect("key-release-event", self._keyReleaseEvent)

    def _initPlayers(self, *event_args: object) -> None:
        clearChildren(self.playerNamesBox)

        for player in self.playerManager.getPlayers():
            points = self.gameStateModel.getPointsOfPlayer(player)
            widget = PlayerWidget(player.name, points)
            widget.get_style_context().add_class("player-" + str(player.id))
            self.playerNamesBox.pack_start(widget, False, False, 0)

    def _onAnswerSelected(self, _grid: AnswerGrid, row: int, col: int) -> None:
        category = list(self.gameStateModel.getCategoryNames())[col]
        answerValue = self.gameStateModel.getAnswers(category)[row]
        question = self.gameStateModel.getQuestion(category, row)
        if question is not None and question.strip() != "":
            print_current_question(category, row, question)

        answer = self.answerFactory.createAnswer(category, answerValue)

        self.showAnswer(answer, row, col)

    def showGrid(self) -> None:
        clear_current_question_box()

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
            rng = RngWindow(upperLimit = playerCount + 1, duration=500, playerCount=playerCount, parent=self)
            rng.present()
            rng.random()

        if event.keyval == Gdk.KEY_F9:
            self.history.undo()

        if event.keyval == Gdk.KEY_F10:
            self.history.redo()

