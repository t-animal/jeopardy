import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject

def keyvalToKey(key):
	return chr(Gdk.keyval_to_unicode(key))

def createSignal(signalName, emittingClass):
	GObject.signal_new(signalName, emittingClass, GObject.SIGNAL_RUN_LAST, GObject.TYPE_PYOBJECT, [])

def clearChildren(widget):
    for child in widget.get_children():
        widget.remove(child)