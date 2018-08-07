import yaml
from collections import OrderedDict

class SpecialField():
    DOUBLE_JEOPARDY = 0
    IMAGE_ANSWER = 1

    def __init__(self, scalar, specialty):
        self.scalar = scalar
        self.specialty = specialty

    def __str__(self):
        return str(self.scalar)

    @staticmethod
    def isSpecialField(field):
        return type(field) == SpecialField

    @staticmethod
    def doubleJeopardyConstructor(loader, node):
         value = loader.construct_scalar(node)
         return SpecialField(value, SpecialField.DOUBLE_JEOPARDY)

    @staticmethod
    def imageAnswerConstructor(loader, node):
         value = loader.construct_scalar(node)
         return SpecialField(value, SpecialField.IMAGE_ANSWER)

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