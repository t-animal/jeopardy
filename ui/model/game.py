import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

import yaml
from collections import OrderedDict

from . import SIG_GAME_MODEL_CHANGED

class Result():

    def __init__(self, player, correct, points):
        self.player = player
        self.correct = correct
        self.points = points

class GameStateModel(GObject.Object):

    def __init__(self):
        GObject.Object.__init__(self)

        self.answersByCategory = {}
        self.results = {}

    def addCategory(self, categoryName, answers):
        if len(self.answersByCategory) > 0:
            expectedAnswerCount = len(next(iter(self.answersByCategory.values())))

            if not len(answers) == expectedAnswerCount:
                raise ValueError("Answer count does not match existing answers!")

        self.answersByCategory[categoryName] = answers
        self.results[categoryName] = [[] for _ in range(len(answers))]
        
        self.emit(SIG_GAME_MODEL_CHANGED)

    def getCategoryNames(self):
        return self.answersByCategory.keys()

    def getAnswers(self, category):
        return self.answersByCategory[category]

    def hasResults(self, category, rowIndex):
        return len(self.results[category][rowIndex]) > 0

    def getResults(self, category, rowIndex):
        return self.results[category][rowIndex]

    def addResult(self, category, rowIndex, player, correct, points):
        self.results[category][rowIndex].append(Result(player, correct, points))
        self.emit(SIG_GAME_MODEL_CHANGED)

    def getPointsOfPlayer(self, player):
        runningSum = 0
        isOfPlayer = lambda result: result.player == player

        for results in self.results.values():
            for result in filter(isOfPlayer, results):
                if result.correct:
                    runningSum += result.points
                else:
                    runningSum -= result.points

        return runningSum

class GameStateLoader():

    def __init__(self, gameStateModel):
        self.gameStateModel = gameStateModel

    def initFromFile(self, filename):
        with open(filename) as stream:
            data = yaml.safe_load(stream)
            self.checkData(data)

            for category in data:
                self.gameStateModel.addCategory(category, data[category])

    def checkData(self, data):
        if not type(data) == OrderedDict:
            raise ValueError("Game tables must be represented as dicts")

        answerCount = -1
        for category, answers in data.items():
            if not type(answers) == list:
                raise ValueError("Answers must be represented as lists")

            if answerCount == -1:
                answerCount = len(answers)
                continue

            if not len(answers) == answerCount:
                raise ValueError("Answer count for category " + category + \
                    " does not match previous categories")