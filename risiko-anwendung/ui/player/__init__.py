from ...util import createSignal

SIG_PLAYER_SETUP_DONE = "playerSetupDone"

from .name_dialog import PlayerNameDialog
from .overview import PlayerOverviewWindow
from .widget import PlayerWidget

createSignal(SIG_PLAYER_SETUP_DONE, PlayerOverviewWindow)