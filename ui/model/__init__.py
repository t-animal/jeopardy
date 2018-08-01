from ..util import createSignal

SIG_PLAYER_MODEL_CHANGED = 'playerModelChanged'

from .player import PlayerManager, Player

createSignal(SIG_PLAYER_MODEL_CHANGED, PlayerManager)