import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

from collections import OrderedDict
import yaml

from .answers import AnswerFactory
from .grid import AnswerGrid

class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Jeopardy")

        self.mainContainer = Gtk.Box()
        self.grid = AnswerGrid()

        self.mainContainer.pack_start(self.grid, True, True, 0)
        self.add(self.mainContainer)

        self.connect("key-release-event", self.onKeyRelease)

    def showGrid(self):
        for child in self.mainContainer.get_children():
            if not child == self.grid:
                self.mainContainer.remove(child)

        self.grid.show()

    def showAnswer(self, answer):
        self.grid.hide()

        self.mainContainer.pack_start(answer, True, True, 0)
        answer.show()

    def onKeyRelease(self, widget, ev, data = None):
        if ev.keyval == Gdk.KEY_Escape:
            self.showGrid()


class MainWindowInitializer():

    def __init__(self, playerManager, mainWindow):
        self.answerFactory = AnswerFactory(playerManager)
        self._mainWindow = mainWindow
        self._grid = mainWindow.grid

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