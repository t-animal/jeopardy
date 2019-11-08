import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

from collections import OrderedDict

from .loader import SpecialField
from .. import SIG_GAME_MODEL_CHANGED
from ..player import Player

class Result():

    def __init__(self, player, correct, points):
        self.player = player
        self.correct = correct
        self.points = points

    def getLabel(self):
        return "{}{} for {}".format("+" if self.correct else "-", self.points, self.player.name)

class NobodyKnewResult():

    def __init__(self):
        self.correct = False
        self.points = 0
        self.player = None

    def getLabel(self):
        return "Meh."

class GameStateModel(GObject.Object):

    def __init__(self):
        GObject.Object.__init__(self)

        self.answersByCategory = OrderedDict()
        self.resultsByCategory = {}

    def addCategory(self, categoryName, answers):
        if len(self.answersByCategory) > 0:
            expectedAnswerCount = len(next(iter(self.answersByCategory.values())))

            if not len(answers) == expectedAnswerCount:
                raise ValueError("Answer count does not match existing answers!")

        self.answersByCategory[categoryName] = answers
        self.resultsByCategory[categoryName] = [[] for _ in range(len(answers))]
        
        self.emit(SIG_GAME_MODEL_CHANGED)

    def getGridSize(self):
        categoryCount = len(self.answersByCategory) 

        if categoryCount == 0:
            return (0,0)

        rowCount = len(next(iter(self.answersByCategory.values())))
        return (rowCount, categoryCount)

    def getCategoryNames(self):
        return self.answersByCategory.keys()

    def getAnswers(self, category):
        return self.answersByCategory[category]

    def hasResults(self, category, rowIndex):
        return len(self.resultsByCategory[category][rowIndex]) > 0

    def getResults(self, category, rowIndex):
        return self.resultsByCategory[category][rowIndex]

    def addResult(self, category, rowIndex, player, correct, points):
        self.resultsByCategory[category][rowIndex].append(Result(player, correct, points))
        self.emit(SIG_GAME_MODEL_CHANGED)
    
    def setNobodyKnew(self, category, rowIndex):
        self.resultsByCategory[category][rowIndex].append(NobodyKnewResult())
        self.emit(SIG_GAME_MODEL_CHANGED)

    def isDoubleJeopardy(self, category, rowIndex):
        answer = self.getAnswers(category)[rowIndex]
        return SpecialField.isSpecialField(answer) and SpecialField.DOUBLE_JEOPARDY in answer.specialties

    def getPointsOfPlayer(self, player):
        runningSum = 0
        isOfPlayer = lambda result: result.player is not None and result.player.key == player.key

        for resultsByRow in self.resultsByCategory.values():
            for results in resultsByRow:
                for result in filter(isOfPlayer, results):
                    if result.correct:
                        runningSum += result.points
                    else:
                        runningSum -= result.points

        return runningSum
