from ..util import createSignal

SIG_GAME_MODEL_CHANGED = 'gameModelChanged'
SIG_PLAYER_MODEL_CHANGED = 'playerModelChanged'

from .player import PlayerManager, Player
from .game import GameStateModel

createSignal(SIG_PLAYER_MODEL_CHANGED, PlayerManager)
createSignal(SIG_GAME_MODEL_CHANGED, GameStateModel)