import yaml

from ..game import NobodyKnewResult
from .. import SIG_PLAYER_MODEL_CHANGED, SIG_GAME_MODEL_CHANGED

class ModelPersistor():

	def __init__(self, playerManager, gameStateModel, filename="log.yml"):
		self.file = open(filename, "a")
		self.playerManager = playerManager
		self.gameStateModel = gameStateModel

		playerManager.connect(SIG_PLAYER_MODEL_CHANGED, self.persistModel)
		gameStateModel.connect(SIG_GAME_MODEL_CHANGED, self.persistModel)

	def persistModel(self, *args):
		state = {}
		self.addPlayersSerializable(state)
		self.addResultsSerializable(state)

		self.file.write(yaml.safe_dump(state, explicit_start = True))
		self.file.flush()

	def addPlayersSerializable(self, state):
		state["players"] = [{"key": p.key, "name": p.name} for p in self.playerManager.getPlayers()]

	def addResultsSerializable(self, state):
		state["results"] = {}
		_, rows = self.gameStateModel.getGridSize()
		for col, category in enumerate(self.gameStateModel.getCategoryNames()):
			for row in range(0, rows):
				if not self.gameStateModel.hasResults(category, row):
					continue

				results = self.gameStateModel.getResults(category, row)
				serializable = []
				for result in results:
					if type(result) == NobodyKnewResult:
						serializable.append(result)
					else:
						serializable.append({"player": result.player.key,
						  	"correct": result.correct,
							"wager": result.points})
				state["results"]["{}/{}".format(row, col)] = serializable


class ModelLoader():

	def __init__(self, playerManager, gameStateModel, filename="log.yml"):
		self.filename = filename
		self.playerManager = playerManager
		self.gameStateModel = gameStateModel

	def loadModel(self):
		with open(self.filename, "r") as file:
			stateDocuments = yaml.safe_load_all(file)

			for state in stateDocuments:
				pass

		if "players" in state:
			self.loadPlayers(state)

		if "results" in state:
			self.loadResults(state)

	def loadPlayers(self, state):
		for player in state["players"]:
			self.playerManager.addPlayer(player["name"], player["key"])

	def loadResults(self, state):
		categories = list(self.gameStateModel.getCategoryNames())
		for index, results in state["results"].items():
			row, col = map(int, index.split("/"))
			for result in results:
				if type(result) == NobodyKnewResult:
					self.gameStateModel.setNobodyKnew(categories[col], row)
				else:
					self.gameStateModel.addResult(categories[col], row, 
						self.playerManager.getPlayerByKey(result["player"]), result["correct"], result["wager"])
