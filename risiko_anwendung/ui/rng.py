import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gtk, Gdk

import random
import threading

def clearChildren(widget):
    for child in widget.get_children():
        widget.remove(child)

class RngWindow(Gtk.Window):

    def __init__(self, totalNumbers = 60, upperLimit = 100, duration = 800, playerCount = None, parent: Gtk.Window | None = None):
        Gtk.Window.__init__(self, title="RNG")
        if parent is not None:
            self.set_transient_for(parent)
            self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.revealer = Gtk.Revealer(expand=True)
        self.add(self.revealer)

        self._closed = False
        self.connect("delete-event", self._on_close)
        self.connect("destroy", self._on_destroy)
        self.connect("key-release-event", self._on_key_release)

        self.totalNumbers = totalNumbers
        self.upperLimit = upperLimit
        self.duration = duration

        self.choices = [
            "NaN",
            "-1",
            "2147483647",
        ]
        if playerCount is not None:
            self.choices.insert(0, str(playerCount + 1))

        self.revealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)

    def _mark_closed(self):
        self._closed = True

    def _on_close(self, *args):
        self._mark_closed()
        return False

    def _on_destroy(self, *args):
        self._mark_closed()

    def _on_key_release(self, _widget: Gtk.Widget, event: Gdk.EventKey) -> bool:
        if event.keyval == Gdk.KEY_Escape:
            self.close()
            return True
        return False

    def random(self) -> None:
        self._randomAnimation(random.choice(self.choices))

    def _randomAnimation(self, finalResult: str):

        def executeUnlessClosed(func):
            def wrapped():
                if self._closed:
                    return
                return func()
            return wrapped

        def hideNumber():
            self.revealer.set_reveal_child(False)

        def getFinalizationClosure(existingLabel):
            def finalizeLastNumber():
                existingLabel.get_style_context().add_class("final-random-number")
            return finalizeLastNumber

        def nextRandom(randomsLeft, oldLabel=None):
            if not oldLabel is None:
                self.revealer.remove(oldLabel)

            if randomsLeft == 0:
                label = Gtk.Label(label=str(finalResult))
                self.revealer.add(label)
                self.revealer.set_reveal_child(True)
                self.revealer.show_all()
                threading.Timer(self.revealer.get_transition_duration()*2/1000,
                    executeUnlessClosed(lambda: GLib.idle_add(getFinalizationClosure(label)))).start()
                return

            label = Gtk.Label(label=str(random.choices(range(1, self.upperLimit))[0]))
            self.revealer.add(label)

            self.revealer.set_transition_duration(self.duration/(randomsLeft**1.2)+1)
            self.revealer.set_reveal_child(True)
            self.revealer.show_all()

            def queue_next():
                nextRandom(randomsLeft - 1, label)

            threading.Timer(self.revealer.get_transition_duration()/1000, executeUnlessClosed(lambda: GLib.idle_add(hideNumber))).start()
            threading.Timer(self.revealer.get_transition_duration()*2/1000, executeUnlessClosed(lambda: GLib.idle_add(queue_next))).start()

        nextRandom(self.totalNumbers)
