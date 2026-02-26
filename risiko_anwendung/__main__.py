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
from risiko_anwendung.ui.console_output import print_controls
from risiko_anwendung.ui.mainview import MainWindow
from risiko_anwendung.ui.answers import AnswerFactory
from risiko_anwendung.ui.player import PlayerOverviewWindow, SIG_PLAYER_SETUP_DONE
from risiko_anwendung.model import GameStateModel, GameStateLoader, PlayerManager, SIG_PLAYER_MODEL_CHANGED
from risiko_anwendung.model.persistor import ModelPersistor, ModelLoader

from risiko_anwendung.model.game.history import HistoryRestorer

def createArgumentParser() -> ArgumentParser:
    parser = ArgumentParser(description = "Jeopardy")
    parser.add_argument("--logFile", required = True, help="Path to the log file to use for saving game state. If you really want to disable logging, you can set this to /dev/null.")
    parser.add_argument("--config", required = True)
    parser.add_argument("--theme", choices=["light", "dark"], required = False, default="dark")
    return parser

def getArguments(argv: Sequence[str]) -> Namespace:
    parser = createArgumentParser()
    return parser.parse_args(argv)

def main(argv: Sequence[str] | None = None) -> int:
    argsList = list(argv) if argv is not None else sys.argv[1:]
    args = getArguments(argsList)

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

    print_controls()

    try:
        Gtk.main()
    except KeyboardInterrupt:
        pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
