import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

from ..util import keyToUnicode, createSignal

SIG_PLAYER_MODEL_CHANGED = 'playerModelChanged'

class Player():

    def __init__(self, name, key):
        self.name = name
        self.key = key

class PlayerManager(GObject.Object):

    def __init__(self):
        GObject.Object.__init__(self)
        self.playersByKey = {}

    def getPlayers(self):
        return self.playersByKey.values()

    def getPlayer(self, key):
        return self.playersByKey[key]

    def getPlayerByKeycode(self, key):
        return self.getPlayer(keyToUnicode(key))
    
    def isPlayerKey(self, key):
        return key in self.playersByKey
    
    def isPlayerKeycode(self, key):
        return keyToUnicode(key) in self.playersByKey

    def addPlayer(self, name, key):
        self.playersByKey[key] = Player(name, key)
        self.emit(SIG_PLAYER_MODEL_CHANGED)

    def removePlayerByKey(self, key):
        del self.playersByKey[key]
        self.emit(SIG_PLAYER_MODEL_CHANGED)


createSignal(SIG_PLAYER_MODEL_CHANGED, PlayerManager)