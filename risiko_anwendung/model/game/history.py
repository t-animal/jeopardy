import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

import copy
from typing import Any

from risiko_anwendung.model import SIG_GAME_MODEL_CHANGED 
from risiko_anwendung.util import deepEqual
from risiko_anwendung.model.types import ResultsByCategory

from risiko_anwendung.model.game.game import GameStateModel

class HistoryRestorer(GObject.Object):

    def __init__(self, gameStateModel: GameStateModel) -> None:
        GObject.Object.__init__(self)
        self.gameStateModel = gameStateModel

        self.undoStack: list[ResultsByCategory] = []
        self.redoStack: list[ResultsByCategory] = []
        self.pushNewState(self.gameStateModel.resultsByCategory)
        self.gameStateChangeHandlerId: int | None = None

        self._registerSignals()

    def _registerSignals(self) -> None:
        self.gameStateChangeHandlerId = self.gameStateModel.connect(SIG_GAME_MODEL_CHANGED, self._onNewState)
    
    def _unregisterSignals(self) -> None:
        if self.gameStateChangeHandlerId is None:
            return

        self.gameStateModel.disconnect(self.gameStateChangeHandlerId)
        self.gameStateChangeHandlerId = None

    def _onNewState(self, *args: object) -> None:
        self.pushNewState(self.gameStateModel.resultsByCategory)
    
    def pushNewState(self, curState: ResultsByCategory) -> None:
        self.undoStack.append(copy.deepcopy(curState))
        self.redoStack = []

    def undo(self) -> None:
        if len(self.undoStack) <= 1:
            return

        oldCurrentState = self.undoStack.pop()
        self.redoStack.append(oldCurrentState)

        newCurrentState = self.undoStack[-1]
        self.gameStateModel.resultsByCategory = copy.deepcopy(newCurrentState)

        self._unregisterSignals()
        self.gameStateModel.emit(SIG_GAME_MODEL_CHANGED)
        self._registerSignals()
    
    def redo(self) -> None:
        if len(self.redoStack) == 0:
            return

        newCurrentState = self.redoStack.pop()
        self.undoStack.append(newCurrentState)

        self.gameStateModel.resultsByCategory = copy.deepcopy(newCurrentState)

        self._unregisterSignals()
        self.gameStateModel.emit(SIG_GAME_MODEL_CHANGED)
        self._registerSignals()
        