import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject

from collections import OrderedDict
from collections.abc import KeysView

from risiko_anwendung.model.game.loader import SpecialField
from risiko_anwendung.model import SIG_GAME_MODEL_CHANGED
from risiko_anwendung.model.player import Player
from risiko_anwendung.model.types import AnswerValue, CategoryAnswers, CategoryName, ResultsByCategory, ResultLike

class Result():

    def __init__(self, player: Player, correct: bool, points: int):
        self.player = player
        self.correct = correct
        self.points = points

    def getLabel(self) -> str:
        return "{}{} for {}".format("+" if self.correct else "-", self.points, self.player.name)

class NobodyKnewResult():

    def __init__(self) -> None:
        self.correct = False
        self.points = 0
        self.player = None

    def getLabel(self) -> str:
        return "Meh."

class GameStateModel(GObject.Object):

    def __init__(self) -> None:
        GObject.Object.__init__(self)

        self.answersByCategory: OrderedDict[CategoryName, CategoryAnswers] = OrderedDict()
        self.resultsByCategory: ResultsByCategory = {}

    def addCategory(self, categoryName: CategoryName, answers: CategoryAnswers) -> None:
        if len(self.answersByCategory) > 0:
            expectedAnswerCount = len(next(iter(self.answersByCategory.values())))

            if not len(answers) == expectedAnswerCount:
                raise ValueError("Answer count does not match existing answers!")

        self.answersByCategory[categoryName] = answers
        self.resultsByCategory[categoryName] = [[] for _ in range(len(answers))]
        
        self.emit(SIG_GAME_MODEL_CHANGED)

    def getGridSize(self) -> tuple[int, int]:
        categoryCount = len(self.answersByCategory) 

        if categoryCount == 0:
            return (0,0)

        rowCount = len(next(iter(self.answersByCategory.values())))
        return (rowCount, categoryCount)

    def getCategoryNames(self) -> KeysView[CategoryName]:
        return self.answersByCategory.keys()

    def getAnswers(self, category: CategoryName) -> CategoryAnswers:
        return self.answersByCategory[category]

    def hasResults(self, category: CategoryName, rowIndex: int) -> bool:
        return len(self.resultsByCategory[category][rowIndex]) > 0

    def getResults(self, category: CategoryName, rowIndex: int) -> list[ResultLike]:
        return self.resultsByCategory[category][rowIndex]

    def addResult(self, category: CategoryName, rowIndex: int, player: Player, correct: bool, points: int) -> None:
        self.resultsByCategory[category][rowIndex].append(Result(player, correct, points))
        self.emit(SIG_GAME_MODEL_CHANGED)
    
    def setNobodyKnew(self, category: CategoryName, rowIndex: int) -> None:
        self.resultsByCategory[category][rowIndex].append(NobodyKnewResult())
        self.emit(SIG_GAME_MODEL_CHANGED)

    def isDoubleJeopardy(self, category: CategoryName, rowIndex: int) -> bool:
        answer = self.getAnswers(category)[rowIndex]
        return SpecialField.isSpecialField(answer) and SpecialField.DOUBLE_JEOPARDY in answer.specialties

    def getPointsOfPlayer(self, player: Player) -> int:
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
