import yaml
from collections import OrderedDict

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