from risiko_anwendung.util import createSignal

SIG_PLAYER_SETUP_DONE = "playerSetupDone"

from risiko_anwendung.ui.player.name_dialog import PlayerNameDialog
from risiko_anwendung.ui.player.overview import PlayerOverviewWindow
from risiko_anwendung.ui.player.widget import PlayerWidget

createSignal(SIG_PLAYER_SETUP_DONE, PlayerOverviewWindow)