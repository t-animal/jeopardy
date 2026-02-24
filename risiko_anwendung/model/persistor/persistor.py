import os
import yaml
from typing import TextIO
from typing import cast

from risiko_anwendung.model.game import GameStateModel
from risiko_anwendung.model.game import NobodyKnewResult
from risiko_anwendung.model.player import PlayerManager
from risiko_anwendung.model import SIG_PLAYER_MODEL_CHANGED, SIG_GAME_MODEL_CHANGED
from risiko_anwendung.model.types import PersistedState, SerializedResultEntry, SerializedScoredResult

class ModelPersistor():

	def __init__(self, playerManager: PlayerManager, gameStateModel: GameStateModel, filename: str = "log.yml") -> None:
		self.file: TextIO = open(filename, "a")
		self.playerManager = playerManager
		self.gameStateModel = gameStateModel

		playerManager.connect(SIG_PLAYER_MODEL_CHANGED, self.persistModel)
		gameStateModel.connect(SIG_GAME_MODEL_CHANGED, self.persistModel)

	def persistModel(self, *args: object) -> None:
		state: PersistedState = {}
		self.addPlayersSerializable(state)
		self.addResultsSerializable(state)

		self.file.write(yaml.safe_dump(state, explicit_start = True))
		self.file.flush()

	def addPlayersSerializable(self, state: PersistedState) -> None:
		state["players"] = [{"key": p.key, "name": p.name} for p in self.playerManager.getPlayers()]

	def addResultsSerializable(self, state: PersistedState) -> None:
		state["results"] = {}
		_, rows = self.gameStateModel.getGridSize()
		for col, category in enumerate(self.gameStateModel.getCategoryNames()):
			for row in range(0, rows):
				if not self.gameStateModel.hasResults(category, row):
					continue

				results = self.gameStateModel.getResults(category, row)
				serializable: list[SerializedResultEntry] = []
				for result in results:
					if isinstance(result, NobodyKnewResult):
						serializable.append(result)
					else:
						scored: SerializedScoredResult = {
							"player": result.player.key,
						  	"correct": result.correct,
							"wager": result.points
						}
						serializable.append(scored)
				state["results"]["{}/{}".format(row, col)] = serializable


class ModelLoader():

	def __init__(self, playerManager: PlayerManager, gameStateModel: GameStateModel, filename: str = "log.yml") -> None:
		self.filename = filename
		self.playerManager = playerManager
		self.gameStateModel = gameStateModel

	def loadModel(self) -> None:
		if not os.path.isfile(self.filename):
			return

		state: object | None = None
		with open(self.filename, "r") as file:
			stateDocuments = yaml.safe_load_all(file)

			for state in stateDocuments:
				pass
		
		if state is None:
			return

		if not isinstance(state, dict):
			return

		persisted_state = cast(PersistedState, state)

		self.loadPlayers(persisted_state)
		self.loadResults(persisted_state)

	def loadPlayers(self, state: PersistedState) -> None:
		if "players" not in state:
			return
		
		for player in state["players"]:
			self.playerManager.addPlayer(player["name"], player["key"])

	def loadResults(self, state: PersistedState) -> None:
		if "results" not in state:
			return
		
		categories = list(self.gameStateModel.getCategoryNames())
		for index, results in state["results"].items():
			row, col = map(int, index.split("/"))
			for result in results:
				if isinstance(result, NobodyKnewResult):
					self.gameStateModel.setNobodyKnew(categories[col], row)
				else:
					self.gameStateModel.addResult(categories[col], row, 
						self.playerManager.getPlayerByKey(result["player"]), result["correct"], result["wager"])
