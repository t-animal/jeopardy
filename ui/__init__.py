import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

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


class Slot(Gtk.Box):
    def __init__(self, amount, answer, doubleJeopardy=False):
        Gtk.Box.__init__(self)
        self.amount = amount
        self.answer = answer

        self.results = []
        self._button = self._createButton()
        self._label = Gtk.Label("")

        self.repack()

    def repack(self):
        if self._button.get_ancestor(Gtk.Box) == self:
            self.remove(self._button)

        if len(self.results) == 0:
            self.pack_start(self._button, True, True, 0)
        else:
            self._label.set_text("\n".join(self.results))
            self.pack_start(self._label, True, True, 0)
            self._label.show()

        self.queue_draw()

    def showAnswer(self, _target):
        #TODO: Show answer window
        self.repack()

    def _createButton(self):
        self._button = Gtk.Button(label = self.amount)
        self._button.connect("clicked", self.showAnswer)
        return self._button
        

if __name__ == "__main__":
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()