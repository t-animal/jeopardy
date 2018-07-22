import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from MainWindow import MainWindow

if __name__ == "__main__":
    win = MainWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()