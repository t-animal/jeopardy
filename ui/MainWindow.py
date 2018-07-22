import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from collections import OrderedDict
import yaml

from Slot import Slot

class MainWindow(Gtk.Window):

    def __init__(self, cols = 5, rows = 5):
        Gtk.Window.__init__(self, title="Jeopardy")
        self._cols = cols
        self._rows = rows

        self.grid = Gtk.Grid()
        self.grid.set_column_homogeneous(True)
        self.grid.set_row_homogeneous(True)
        self.add(self.grid)

        self._initGrid()

    def _initGrid(self):
        self.headline = tuple([Gtk.Button(label="Headline " + str(i)) for i in range(1, self._rows + 1)])

        getRow = lambda row: tuple([Slot(100 * (row + 1), None) for i in range(0, self._cols)])
        self.slots = tuple([getRow(row) for row in range(0, self._rows)])

        for child in self.grid.get_children():
            self.grid.remove(child)

        for col in range(0, self._cols):
            self.grid.attach(self.headline[col], col, 0, 1, 1)
            for row in range(0, self._rows):
                self.grid.attach(self.slots[row][col], col, row + 1, 1, 1)

class MainWindowInitializer():

    def __init__(self, mainWindow):
        self._mainWindow = mainWindow

    def initFromFile(self, filename):
        with open(filename) as stream:
            data = yaml.safe_load(stream)
            gridSize = self.getGridSize(data)

            if not (self._mainWindow._rows, self._mainWindow._cols) == gridSize:
                self._mainWindow._rows, self._mainWindow._cols = gridSize
                self._mainWindow._initGrid()

            categories = list(data.keys())
            for col in range(0, self._mainWindow._cols):
                self._mainWindow.headline[col].set_label(categories[col])
                for row in range(0,  self._mainWindow._rows):
                    self._mainWindow.slots[row][col].answer = data[categories[col]][row]
                    self._mainWindow.slots[row][col].repack()

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