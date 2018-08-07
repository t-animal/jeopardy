import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from .grid import AnswerGrid
from .buzz_indicator import BuzzIndicator
from .wager_prompt import WagerPrompt

from ..player import PlayerWidget
from ..answers import AnswerFactory

from ...model import SIG_PLAYER_MODEL_CHANGED, SIG_GAME_MODEL_CHANGED
from ...util import clearChildren

class MainWindow(Gtk.Window):

    def __init__(self, playerManager, gameStateModel):
        Gtk.Window.__init__(self, title="Jeopardy")
        self.buzzIndicator = None
        self.buzzerSignalId = None

        self.playerManager = playerManager
        self.gameStateModel = gameStateModel

        self.mainContainer = Gtk.Box()

        self.gridContainer = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.grid = AnswerGrid()
        self.playerNamesBox = Gtk.Box()

        self.gridContainer.pack_start(self.grid, True, True, 0)
        self.gridContainer.pack_end(self.playerNamesBox, False, False, 0)

        self.mainContainer.pack_start(self.gridContainer, True, True, 0)
        self.add(self.mainContainer)

        self.connect("key-release-event", self.onKeyRelease)

    def showGrid(self):
        for child in self.mainContainer.get_children():
            if not child == self.gridContainer:
                self.mainContainer.remove(child)

        self.gridContainer.show()

    def showAnswer(self, answer, row, col):
        category = list(self.gameStateModel.getCategoryNames())[col]

        wager = (row + 1) * 100
        if self.gameStateModel.isDoubleJeopardy(category, row):
            wagerPrompt = WagerPrompt(self)
            wagerPrompt.run()
            wager = int(wagerPrompt.wagerInput.get_value())
            wagerPrompt.destroy()

        self.gridContainer.hide()

        self.mainContainer.pack_start(answer, True, True, 0)
        self.buzzerSignalId = self.connect("key-release-event", self.buzzered, row, col, wager)
        answer.show()

    def buzzered(self, widget, event, row, col, wager = 0):
        if self.playerManager.isPlayerKeyval(event.keyval) and self.buzzIndicator is None:
            activePlayer = self.playerManager.getPlayerByKeyval(event.keyval)
            self.buzzIndicator = BuzzIndicator(activePlayer)
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

                if not self.buzzerSignalId is None:
                    self.disconnect(self.buzzerSignalId)
                    self.buzzerSignalId = None

    def onKeyRelease(self, widget, event, data = None):
        if event.keyval == Gdk.KEY_Escape:
            self.showGrid()
            return

class MainWindowInitializer():

    def __init__(self, playerManager, gameStateModel, mainWindow):
        self.answerFactory = AnswerFactory(playerManager)
        self.playerManager = playerManager
        self.gameStateModel = gameStateModel
        self._mainWindow = mainWindow
        self._grid = mainWindow.grid

        playerManager.connect(SIG_PLAYER_MODEL_CHANGED, self.initPlayers)
        gameStateModel.connect(SIG_GAME_MODEL_CHANGED, self.initGrid)
        gameStateModel.connect(SIG_GAME_MODEL_CHANGED, self.initPlayers)

    def initMainWindow(self):
        self.initPlayers()
        self.initGrid()

    def initPlayers(self, *event_args):
        clearChildren(self._mainWindow.playerNamesBox)

        for player in self.playerManager.getPlayers():
            points = self.gameStateModel.getPointsOfPlayer(player)
            self._mainWindow.playerNamesBox.add(PlayerWidget(player.name, points))

    def initGrid(self, *event_args):
        cols = len(self.gameStateModel.getCategoryNames())

        for col, category in enumerate(self.gameStateModel.getCategoryNames()):
            answers = self.gameStateModel.getAnswers(category)

            if not self._grid.rows == len(answers) or not self._grid.cols == cols:
                self._grid.initComponents(len(answers), cols)

            self._grid.headline[col].set_label(category)
            for row, answer in enumerate(self.gameStateModel.getAnswers(category)):
                self._grid.slots[row][col].answer = self.answerFactory.createAnswer(category, answer)
                self._grid.slots[row][col].results = self.gameStateModel.getResults(category, row)
                self._grid.slots[row][col].repack()

