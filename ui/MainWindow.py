import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from Slot import Slot

class MainWindow(Gtk.Window):

    def __init__(self, cols = 5, rows = 5):
        Gtk.Window.__init__(self, title="Jeopardy")

        self.headline = tuple([Gtk.Button(label="Headline " + str(i)) for i in range(1, rows+1)])

        getRow = lambda row: tuple([Slot(100 * (row + 1), None) for i in range(0, cols)])
        self.slots = tuple([getRow(row) for row in range(0, rows)])

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)
        self.add(grid)

        for col in range(0, cols):
            grid.attach(self.headline[col], col, 0, 1, 1)
            for row in range(0, rows):
                grid.attach(self.slots[row][col], col, row + 1, 1, 1)
