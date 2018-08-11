import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

import sys, os

from .ui.fullscreeen_manager import FullscreenManager
from .ui.mainview import MainWindow, MainWindowInitializer
from .ui.player import PlayerOverviewWindow, SIG_PLAYER_SETUP_DONE
from .model import GameStateModel, GameStateLoader, PlayerManager, SIG_PLAYER_MODEL_CHANGED
from .model.persistor import ModelPersistor, ModelLoader


if __name__ == "__main__":
    fullscreenManager =  FullscreenManager()
    playerManager = PlayerManager()
    gameStateModel = GameStateModel()

    GameStateLoader(gameStateModel).initFromFile("test.yaml")

    ModelLoader(playerManager, gameStateModel).loadModel()
    ModelPersistor(playerManager, gameStateModel)

    mainWindow = MainWindow(playerManager, gameStateModel)
    playerWindow = PlayerOverviewWindow(playerManager)

    initer = MainWindowInitializer(playerManager, gameStateModel, mainWindow)
    initer.initMainWindow()

    fullscreenManager.handleWindow(mainWindow)
    fullscreenManager.handleWindow(playerWindow)

    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    style_provider = Gtk.CssProvider()
    style_provider.load_from_path(dir_path + "/custom.css")

    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(),
        style_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    mainWindow.show_all()
    playerWindow.show_all()

    mainWindow.iconify()
    playerWindow.present()

    mainWindow.connect("destroy", Gtk.main_quit)
    playerWindow.connect(SIG_PLAYER_SETUP_DONE, lambda x: mainWindow.present())

    try:
        Gtk.main()
    except KeyboardInterrupt:
        pass
    