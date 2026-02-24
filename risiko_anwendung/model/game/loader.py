import itertools
import os
import yaml
from collections import OrderedDict
from typing import TYPE_CHECKING, Callable, TypeAlias, TypeGuard

from risiko_anwendung.model.types import AnswerValue, GameTable, QuestionText, QuestionsByCategory

if TYPE_CHECKING:
    from risiko_anwendung.model.game.game import GameStateModel

from yaml import Loader, ScalarNode

SpecialFieldConstructor: TypeAlias = Callable[[Loader, ScalarNode], "SpecialField"]

class SpecialField():
    DOUBLE_JEOPARDY = 0
    IMAGE_ANSWER = 1
    AUDIO_ANSWER = 2

    def __init__(self, scalar: str, specialty: int):
        self.scalar = scalar
        self.specialties: list[int] = [specialty]

    def __str__(self) -> str:
        return str(self.scalar)

    def isImage(self) -> bool:
        return SpecialField.IMAGE_ANSWER in self.specialties

    def isAudio(self) -> bool:
        return SpecialField.AUDIO_ANSWER in self.specialties

    @staticmethod
    def isSpecialField(field: object) -> TypeGuard["SpecialField"]:
        return isinstance(field, SpecialField)

    @staticmethod
    def makeDoubleJeopardyAndConstructor(wrappedConstructor: SpecialFieldConstructor) -> SpecialFieldConstructor:
        def newConstructor(loader: Loader, node: ScalarNode)-> SpecialField:
            wrapped_node: SpecialField = wrappedConstructor(loader, node)
            wrapped_node.specialties += [SpecialField.DOUBLE_JEOPARDY]
            return wrapped_node

        return newConstructor

    @staticmethod
    def doubleJeopardyConstructor(loader: Loader, node: ScalarNode) -> "SpecialField":
         value = loader.construct_scalar(node)
         return SpecialField(value, SpecialField.DOUBLE_JEOPARDY)

    @staticmethod
    def imageAnswerConstructor(loader: Loader, node: ScalarNode)-> "SpecialField":
         value = loader.construct_scalar(node)
         return SpecialField(value, SpecialField.IMAGE_ANSWER)

    @staticmethod
    def audioAnswerConstructor(loader: Loader, node: ScalarNode)-> "SpecialField":
        value = loader.construct_scalar(node)
        return SpecialField(value, SpecialField.AUDIO_ANSWER)

class GameStateLoader():

    def __init__(self, gameStateModel: "GameStateModel"):
        self.gameStateModel = gameStateModel

    def initFromFile(self, filename: str) -> None:
        with open(filename) as stream:
            gameTable, questionsByCategory = self.checkData(yaml.safe_load(stream))

            folder = os.path.dirname(os.path.abspath(filename))
            for answer in itertools.chain(*gameTable.values()):
                if SpecialField.isSpecialField(answer) and (answer.isImage() or answer.isAudio()):
                    answer.scalar = os.path.join(folder, answer.scalar)

            for category in gameTable:
                self.gameStateModel.addCategory(category, gameTable[category], questionsByCategory[category])

    def checkData(self, data: object) -> tuple[GameTable, QuestionsByCategory]:
        if not isinstance(data, OrderedDict):
            raise ValueError("Game tables must be represented as dicts")

        gameTable: GameTable = OrderedDict()
        questionsByCategory: QuestionsByCategory = {}
        answerCount = -1
        for category, answers in data.items():
            if not isinstance(category, str):
                raise ValueError("Category names must be represented as strings")

            if not isinstance(answers, list):
                raise ValueError("Answers must be represented as lists")

            normalizedAnswers: list[AnswerValue] = []
            normalizedQuestions: list[QuestionText] = []
            for answer in answers:
                answerValue, question = self._normalizeAnswer(answer)
                normalizedAnswers.append(answerValue)
                normalizedQuestions.append(question)

            if answerCount == -1:
                answerCount = len(normalizedAnswers)
            elif len(normalizedAnswers) != answerCount:
                raise ValueError("Answer count for category " + category + \
                    " does not match previous categories")

            gameTable[category] = normalizedAnswers
            questionsByCategory[category] = normalizedQuestions

        return gameTable, questionsByCategory

    def _normalizeAnswer(self, clue: object) -> tuple[AnswerValue, QuestionText]:
        if isinstance(clue, (str, SpecialField)):
            return clue, None

        if not isinstance(clue, dict):
            raise ValueError("Answers must be strings, special fields, or mappings with keys 'answer' and optional 'question'")

        unsupportedKeys = [key for key in clue.keys() if key not in ["answer", "question"]]
        if unsupportedKeys:
            raise ValueError("Unsupported keys in answer mapping: " + ", ".join(map(str, unsupportedKeys)))

        if "answer" not in clue:
            raise ValueError("Answer mappings must contain an 'answer' key")

        answerValue = clue["answer"]
        if not isinstance(answerValue, (str, SpecialField)):
            raise ValueError("The 'answer' value must be a string or special field")

        questionValue = clue.get("question")
        if questionValue is not None and not isinstance(questionValue, str):
            raise ValueError("The optional 'question' value must be a string")

        return answerValue, questionValue
