import itertools
import os
import yaml
from collections import OrderedDict
from typing import TYPE_CHECKING, Callable, TypeAlias, TypeGuard

from risiko_anwendung.model.types import GameTable

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
            data = self.checkData(yaml.safe_load(stream))

            folder = os.path.dirname(os.path.abspath(filename))
            for answer in itertools.chain(*data.values()):
                if SpecialField.isSpecialField(answer) and (answer.isImage() or answer.isAudio()):
                    answer.scalar = os.path.join(folder, answer.scalar)

            for category in data:
                self.gameStateModel.addCategory(category, data[category])

    def checkData(self, data: object) -> GameTable:
        if not isinstance(data, OrderedDict):
            raise ValueError("Game tables must be represented as dicts")

        answerCount = -1
        for category, answers in data.items():
            if not isinstance(category, str):
                raise ValueError("Category names must be represented as strings")

            if not isinstance(answers, list):
                raise ValueError("Answers must be represented as lists")

            for answer in answers:
                if not isinstance(answer, (str, SpecialField)):
                    raise ValueError("Answers must be strings or special fields (double jeopardy, image answer, audio answer)")

            if answerCount == -1:
                answerCount = len(answers)
                continue

            if not len(answers) == answerCount:
                raise ValueError("Answer count for category " + category + \
                    " does not match previous categories")

        return data
