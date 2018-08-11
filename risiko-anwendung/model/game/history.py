import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

import copy

from .. import SIG_GAME_MODEL_CHANGED 
from ...util import deepEqual

class HistoryRestorer(GObject.Object):

    def __init__(self, gameStateManager):
        GObject.Object.__init__(self)
        self.gameStateManager = gameStateManager

        self.history = []
        self.curSelected = -1
        self.pushNewState(self.gameStateManager.resultsByCategory)
        self.gameStateChangeHandlerId = None 

        self._registerSignals()

    def _registerSignals(self):
        self.gameStateChangeHandlerId = self.gameStateManager.connect(SIG_GAME_MODEL_CHANGED, self._onNewState)
    
    def _unregisterSignals(self):
        if self.gameStateChangeHandlerId is None:
            return

        self.gameStateManager.disconnect(self.gameStateChangeHandlerId)
        self.gameStateChangeHandlerId = None

    def _onNewState(self, *args):
        self.pushNewState(self.gameStateManager.resultsByCategory)
    
    def pushNewState(self, curState):
        self.history.append(copy.deepcopy(curState))
        self.curSelected += 1

    def undo(self):
        if self.curSelected == 0:
            return
        
        self.curSelected  -= 1

        self.gameStateManager.resultsByCategory = self.history[self.curSelected]
        self._unregisterSignals()
        self.gameStateManager.emit(SIG_GAME_MODEL_CHANGED)
        self._registerSignals()
    
    def redo(self):
        if self.curSelected == len(self.history) - 1:
            return
        
        self.curSelected  += 1
        
        self.gameStateManager.resultsByCategory = self.history[self.curSelected]
        self._unregisterSignals()
        self.gameStateManager.emit(SIG_GAME_MODEL_CHANGED)
        self._registerSignals()
        