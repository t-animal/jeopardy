import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

import sys, os
from argparse import ArgumentParser

from .ui.fullscreeen_manager import FullscreenManager
from .ui.mainview import MainWindow, MainWindowInitializer
from .ui.player import PlayerOverviewWindow, SIG_PLAYER_SETUP_DONE
from .model import GameStateModel, GameStateLoader, PlayerManager, SIG_PLAYER_MODEL_CHANGED
from .model.persistor import ModelPersistor, ModelLoader

def getArguments(argv):
    parser = ArgumentParser(description = "Jeopardy")
    parser.add_argument("--logFile")
    parser.add_argument("--config")
    parser.add_argument("--theme", choices=["light", "dark"], required = False, default="dark")
    return parser.parse_args(argv)

if __name__ == "__main__":
    args = getArguments(sys.argv[1:])

    fullscreenManager =  FullscreenManager()
    playerManager = PlayerManager()
    gameStateModel = GameStateModel()

    GameStateLoader(gameStateModel).initFromFile(args.config)

    ModelLoader(playerManager, gameStateModel, args.logFile).loadModel()
    ModelPersistor(playerManager, gameStateModel, args.logFile)

    mainWindow = MainWindow(playerManager, gameStateModel)
    playerWindow = PlayerOverviewWindow(playerManager)

    initer = MainWindowInitializer(playerManager, gameStateModel, mainWindow)
    initer.initMainWindow()

    fullscreenManager.handleWindow(mainWindow)
    fullscreenManager.handleWindow(playerWindow)

    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    style_provider = Gtk.CssProvider()

    if args.theme == "dark":
        style_provider.load_from_path(dir_path + "/custom.css")
    else:
        style_provider.load_from_path(dir_path + "/custom-light.css")

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
    