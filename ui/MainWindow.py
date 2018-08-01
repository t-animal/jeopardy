import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from collections import OrderedDict
import yaml

from .answers import AnswerFactory
from .player import PlayerWidget
from .grid import AnswerGrid
from .model import SIG_PLAYER_MODEL_CHANGED
from .util import clearChildren

class MainWindow(Gtk.Window):

    def __init__(self, playerManager):
        Gtk.Window.__init__(self, title="Jeopardy")
        self.buzzIndicator = None

        self.playerManager = playerManager

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

    def showAnswer(self, answer):
        self.gridContainer.hide()

        self.mainContainer.pack_start(answer, True, True, 0)
        answer.show()

    def onKeyRelease(self, widget, event, data = None):
        if event.keyval == Gdk.KEY_Escape:
            self.showGrid()
            return

        if self.playerManager.isPlayerKeyval(event.keyval) and self.buzzIndicator is None:
            self.buzzIndicator = QuestionRequestWindow(self.playerManager.getPlayerByKeyval(event.keyval))
            self.buzzIndicator.placeAtBottomRightOf(self)
            self.buzzIndicator = None
            

class QuestionRequestWindow(Gtk.Window):

    def __init__(self, player):
        Gtk.Window.__init__(self)

        self.buttonContainer = Gtk.Box()
        self.buttonContainer.pack_end(Gtk.Button(label = "Oops"), False, False, 0)
        self.buttonContainer.pack_end(Gtk.Button(label = "Correct"), False, False, 0)
        self.buttonContainer.pack_end(Gtk.Button(label = "Wrong!"), False, False, 0)

        self.mainContainer = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.mainContainer.pack_start(Gtk.Label(player.name + " has buzzered"), True, True, 0)
        self.mainContainer.pack_end(self.buttonContainer, True, True, 0)

        self.add(self.mainContainer)

        self.show_all()

        self.set_decorated(False)
        self.set_keep_above(True)

    def placeAtBottomRightOf(self, otherWindow):
        otherX, otherY = otherWindow.get_position()
        otherWidth, otherHeight = otherWindow.get_size()
        selfWidth, selfHeight = self.get_size()

        self.move(otherX + otherWidth - selfWidth, otherY + otherHeight - selfHeight)


class MainWindowInitializer():

    def __init__(self, playerManager, mainWindow):
        self.answerFactory = AnswerFactory(playerManager)
        self.playerManager = playerManager
        self._mainWindow = mainWindow
        self._grid = mainWindow.grid
        playerManager.connect(SIG_PLAYER_MODEL_CHANGED, self.initPlayers)

    def initFromFile(self, filename):
        with open(filename) as stream:
            data = yaml.safe_load(stream)
            rows, cols = self.getGridSize(data)

            if not self._grid.rows == rows or not self._grid.cols == cols:
                self._grid.initComponents(rows, cols)

            categories = list(data.keys())
            for col in range(0, cols):
                self._grid.headline[col].set_label(categories[col])

                for row in range(0, rows):
                    answer = self.answerFactory.createAnswer(categories[col], data[categories[col]][row])
                    self._grid.slots[row][col].answer = answer

    def initPlayers(self, data):
        clearChildren(self._mainWindow.playerNamesBox)

        for player in self.playerManager.getPlayers():
            self._mainWindow.playerNamesBox.add(PlayerWidget(player.name))


    def getGridSize(self, data):
        if not type(data) == OrderedDict:
            raise ValueError("Game tables must be represented as dicts")

        answerCount = -1
        for category, answers in data.items():
            if not type(answers) == list:
                raise ValueError("Answers must be represented as lists")

            if answerCount == -1:
                answerCount = len(answers)
                continue

            if not len(answers) == answerCount:
                raise ValueError("Answer count for category " + category + \
                    " does not match previous categories")

        return (answerCount, len(data))

from yaml import SafeLoader, SafeDumper
from yaml.representer import SafeRepresenter
_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG

def dict_representer(dumper, data):
    return dumper.represent_dict(data.iteritems())


def dict_constructor(loader, node):
    return OrderedDict(loader.construct_pairs(node))

SafeDumper.add_representer(OrderedDict, dict_representer)
SafeLoader.add_constructor(_mapping_tag, dict_constructor)

SafeDumper.add_representer(str, SafeRepresenter.represent_str)