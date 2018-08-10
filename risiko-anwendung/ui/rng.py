import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gtk, Gdk

import random
import threading

def clearChildren(widget):
    for child in widget.get_children():
        widget.remove(child)

class RngWindow(Gtk.Window):

    def __init__(self, totalNumbers = 40, upperLimit = 100, duration = 800):
        Gtk.Window.__init__(self, title="RNG")
        self.revealer = Gtk.Revealer(expand=True)
        self.add(self.revealer)

        self.totalNumbers = 60
        self.upperLimit = upperLimit
        self.duration = duration

        self.revealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
    
    def random(self, number = 42):

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
                label = Gtk.Label(str(number))
                self.revealer.add(label)
                self.revealer.set_reveal_child(True)
                self.revealer.show_all()
                threading.Timer(self.revealer.get_transition_duration()*2/1000,
                    lambda: GLib.idle_add(getFinalizationClosure(label))).start()
                return
            
            label = Gtk.Label(str(random.choices(range(1, self.upperLimit))[0]))
            self.revealer.add(label)

            self.revealer.set_transition_duration(self.duration/(randomsLeft**1.2)+1)
            self.revealer.set_reveal_child(True)
            self.revealer.show_all()

            def queue_next():
                nextRandom(randomsLeft - 1, label)
            
            threading.Timer(self.revealer.get_transition_duration()/1000, lambda: GLib.idle_add(hideNumber)).start()
            threading.Timer(self.revealer.get_transition_duration()*2/1000, lambda: GLib.idle_add(queue_next)).start()
        
        nextRandom(self.totalNumbers)
