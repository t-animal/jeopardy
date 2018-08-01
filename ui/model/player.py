import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

from collections import OrderedDict

from . import SIG_PLAYER_MODEL_CHANGED
from ..util import keyvalToKey

class Player():

    def __init__(self, name, key):
        self.name = name
        self.key = key

class PlayerManager(GObject.Object):

    def __init__(self):
        GObject.Object.__init__(self)
        self.playersByKey = OrderedDict()

    def getPlayers(self):
        return self.playersByKey.values()

    def getPlayer(self, key):
        return self.playersByKey[key]

    def getPlayerByKeyval(self, keyval):
        return self.getPlayer(keyvalToKey(keyval))
    
    def isPlayerKey(self, key):
        return key in self.playersByKey
    
    def isPlayerKeyval(self, keyval):
        return keyvalToKey(keyval) in self.playersByKey

    def addPlayer(self, name, key):
        self.playersByKey[key] = Player(name, key)
        self.emit(SIG_PLAYER_MODEL_CHANGED)

    def removePlayerByKey(self, key):
        del self.playersByKey[key]
        self.emit(SIG_PLAYER_MODEL_CHANGED)

