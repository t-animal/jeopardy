from ...util import createSignal

SIG_PLAYER_SETUP_DONE = "playerSetupDone"

from .PlayerNameDialog import PlayerNameDialog
from .PlayerOverviewWindow import PlayerOverviewWindow
from .PlayerWidget import PlayerWidget

createSignal(SIG_PLAYER_SETUP_DONE, PlayerOverviewWindow)