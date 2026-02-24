import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject

import json
from typing import Any, Sequence

def keyvalToKey(key: int) -> str:
	return chr(Gdk.keyval_to_unicode(key))

def createSignal(signalName: str, emittingClass: type[object], paramTypes: Sequence[object] | None = None) -> None:
    if paramTypes is None:
        paramTypes = []
    GObject.signal_new(signalName, emittingClass, GObject.SIGNAL_RUN_LAST, GObject.TYPE_PYOBJECT, list(paramTypes))

def clearChildren(widget: Gtk.Container) -> None:
    for child in widget.get_children():
        widget.remove(child)

def deepEqual(arg1: Any, arg2: Any) -> bool:
    return json.dumps(arg1) == json.dumps(arg2)