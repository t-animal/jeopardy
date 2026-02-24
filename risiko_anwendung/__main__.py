"""Entry point for the Jeopardy GTK application.

Python 3.14 removed `pkgutil.get_loader`, but some PyGObject versions still
import it. Provide a small compatibility shim so the app can start.
"""

import importlib.util
import pkgutil
from argparse import ArgumentParser, Namespace
from collections.abc import Sequence
from importlib.abc import Loader

if not hasattr(pkgutil, "get_loader"):
    def get_loader(fullname: str) -> Loader | None:
        try:
            spec = importlib.util.find_spec(fullname)
        except (ImportError, ValueError):
            return None
        return spec.loader if spec else None

    setattr(pkgutil, "get_loader", get_loader)

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

import sys, os

from risiko_anwendung.ui.fullscreeen_manager import FullscreenManager
from risiko_anwendung.ui.mainview import MainWindow
from risiko_anwendung.ui.answers import AnswerFactory
from risiko_anwendung.ui.player import PlayerOverviewWindow, SIG_PLAYER_SETUP_DONE
from risiko_anwendung.model import GameStateModel, GameStateLoader, PlayerManager, SIG_PLAYER_MODEL_CHANGED
from risiko_anwendung.model.persistor import ModelPersistor, ModelLoader

from risiko_anwendung.model.game.history import HistoryRestorer

def getArguments(argv: Sequence[str]) -> Namespace:
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

    history = HistoryRestorer(gameStateModel)
    answerFactory = AnswerFactory(playerManager)

    mainWindow = MainWindow(playerManager, gameStateModel, history, answerFactory)
    playerWindow = PlayerOverviewWindow(playerManager)

    fullscreenManager.handleWindow(mainWindow)
    fullscreenManager.handleWindow(playerWindow)

    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)
    style_provider = Gtk.CssProvider()

    if args.theme == "dark":
        style_provider.load_from_path(dir_path + "/custom.css")
    else:
        style_provider.load_from_path(dir_path + "/custom-light.css")

    screen = Gdk.Screen.get_default()
    if screen is not None:
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    mainWindow.show_all()
    playerWindow.show_all()

    mainWindow.iconify()
    playerWindow.present()

    mainWindow.connect("destroy", Gtk.main_quit)
    
    def beginGame(*args: object) -> None:
        mainWindow.present()
        playerWindow.iconify()

    playerWindow.connect(SIG_PLAYER_SETUP_DONE, beginGame)

    print("""
        Keys on main screen:
            ESC: Close current question/"Oops" button
            F7: Toggle audio playback for current question
            F8: Set current question to "nobody knew it"
            F9: Undo last action
            F10: Redo last undone action
            F11: Fullscreen (only on second monitor if available)
            F12: Display the "RNG"
            <Player key>: A player wants to answer
    """)

    try:
        Gtk.main()
    except KeyboardInterrupt:
        pass
    