import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject

import unicodedata

from risiko_anwendung.ui.player import PlayerNameDialog, SIG_PLAYER_SETUP_DONE
from risiko_anwendung.model.player import PlayerManager
from risiko_anwendung.util import keyvalToKey

class PlayerOverviewWindow(Gtk.Window):

    def __init__(self, playerManager: PlayerManager):
        Gtk.Window.__init__(self, title = "Player Overview")
        self.playerListStore =  Gtk.ListStore(str, str)
        self.playerManager = playerManager

        playerListRenderer = Gtk.CellRendererText()
        self.playerList = Gtk.TreeView(model=self.playerListStore)
        self.playerList.append_column(Gtk.TreeViewColumn("Name", playerListRenderer, text=0))
        self.playerList.append_column(Gtk.TreeViewColumn("Key", playerListRenderer, text=1))
        self.playerList.set_enable_search(False)
        self.playerList.set_headers_visible(True)

        self.beginButton = Gtk.Button(label="Begin!")
        self.beginButton.connect("clicked", lambda x: self.emit(SIG_PLAYER_SETUP_DONE))
        
        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.VERTICAL)
        box.pack_start(Gtk.Label(label="Player management"), False, False, 0)
        box.pack_start(self.playerList, True, True, 0)
        box.pack_start(Gtk.Label(label="Press any key to add a new player"), False, False, 0)
        box.pack_end(self.beginButton, False, False, 0)

        self.connect("key-release-event", self._onKeyRelease)
        self.add(box)
        self.resize(500, 400)

        self.updateList()

    def askName(self, key: str) -> None:
        existingName = ""
        if self.playerManager.isPlayerKey(key):
            existingName = self.playerManager.getPlayer(key).name

        dialog = PlayerNameDialog(self, key, existingName)
        response = dialog.run()
        dialog.hide()

        if response == Gtk.ResponseType.OK and not dialog.getName().strip() == "":
            self.playerManager.addPlayer(dialog.getName().strip(), key)
            self.updateList()
        
        self.beginButton.grab_focus()

    def removeSelectedPlayer(self) -> None:
        model, treeiter = self.playerList.get_selection().get_selected()
        if treeiter is None:
            return

        self.playerManager.removePlayerByKey(model[treeiter][1])
        self.updateList()

    def updateList(self) -> None:
        self.playerListStore.clear()

        for player in self.playerManager.getPlayers():
            self.playerListStore.append([player.name, player.key])

    def _onKeyRelease(self, widget: Gtk.Widget, event: Gdk.EventKey, data: object | None = None) -> None:
        if event.keyval == Gdk.KEY_Delete:
            self.removeSelectedPlayer()
            return

        pressedKey = keyvalToKey(event.keyval)
        keyCategory = unicodedata.category(pressedKey)

        if keyCategory[0] in ["L", "M", "N", "P", "S"]:
            self.askName(pressedKey)
        else:
            print("Possibly illegal character: {} in {} from {}".format(pressedKey, 
                keyCategory, Gdk.keyval_name(event.keyval)))