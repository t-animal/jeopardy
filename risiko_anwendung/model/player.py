import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

from collections import OrderedDict
from collections.abc import ValuesView

from risiko_anwendung.model import SIG_PLAYER_MODEL_CHANGED
from risiko_anwendung.model.types import PlayerKey
from risiko_anwendung.util import keyvalToKey

class Player():
    RUNNING_ID = 0

    def __init__(self, name: str, key: PlayerKey):
        self.name = name
        self.key = key
        self.id = Player.RUNNING_ID
        Player.RUNNING_ID += 1


class PlayerManager(GObject.Object):

    def __init__(self) -> None:
        GObject.Object.__init__(self)
        self.playersByKey: OrderedDict[PlayerKey, Player] = OrderedDict()

    def getPlayers(self) -> ValuesView[Player]:
        return self.playersByKey.values()

    def getPlayer(self, key: PlayerKey) -> Player:
        return self.playersByKey[key]

    def getPlayerByKeyval(self, keyval: int) -> Player:
        return self.getPlayer(keyvalToKey(keyval))

    def getPlayerByKey(self, key: PlayerKey) -> Player:
        return self.getPlayer(key)
    
    def isPlayerKey(self, key: PlayerKey) -> bool:
        return key in self.playersByKey
    
    def isPlayerKeyval(self, keyval: int) -> bool:
        return keyvalToKey(keyval) in self.playersByKey

    def addPlayer(self, name: str, key: PlayerKey) -> None:
        self.playersByKey[key] = Player(name, key)
        self.emit(SIG_PLAYER_MODEL_CHANGED)

    def removePlayerByKey(self, key: PlayerKey) -> None:
        del self.playersByKey[key]
        self.emit(SIG_PLAYER_MODEL_CHANGED)

