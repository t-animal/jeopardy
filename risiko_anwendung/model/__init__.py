from risiko_anwendung.util import createSignal

SIG_GAME_MODEL_CHANGED = 'gameModelChanged'
SIG_PLAYER_MODEL_CHANGED = 'playerModelChanged'

from risiko_anwendung.model.player import PlayerManager, Player
from risiko_anwendung.model.game import GameStateModel, GameStateLoader

createSignal(SIG_PLAYER_MODEL_CHANGED, PlayerManager)
createSignal(SIG_GAME_MODEL_CHANGED, GameStateModel)