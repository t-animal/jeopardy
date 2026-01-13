import itertools
import os
import yaml
from collections import OrderedDict

class SpecialField():
    DOUBLE_JEOPARDY = 0
    IMAGE_ANSWER = 1
    AUDIO_ANSWER = 2

    def __init__(self, scalar, specialty):
        self.scalar = scalar
        self.specialties = [specialty]

    def __str__(self):
        return str(self.scalar)

    def isImage(self):
        return SpecialField.IMAGE_ANSWER in self.specialties

    def isAudio(self):
        return SpecialField.AUDIO_ANSWER in self.specialties

    @staticmethod
    def isSpecialField(field):
        return type(field) == SpecialField

    @staticmethod
    def makeDoubleJeopardyAndConstructor(wrappedConstructor):
        def newConstructor(loader, node):
            node = wrappedConstructor(loader, node)
            node.specialties += [SpecialField.DOUBLE_JEOPARDY]
            return node
        
        return newConstructor

    @staticmethod
    def doubleJeopardyConstructor(loader, node):
         value = loader.construct_scalar(node)
         return SpecialField(value, SpecialField.DOUBLE_JEOPARDY)

    @staticmethod
    def imageAnswerConstructor(loader, node):
         value = loader.construct_scalar(node)
         return SpecialField(value, SpecialField.IMAGE_ANSWER)

    @staticmethod
    def audioAnswerConstructor(loader, node):
        value = loader.construct_scalar(node)
        return SpecialField(value, SpecialField.AUDIO_ANSWER)

class GameStateLoader():

    def __init__(self, gameStateModel):
        self.gameStateModel = gameStateModel

    def initFromFile(self, filename):
        with open(filename) as stream:
            data = yaml.safe_load(stream)
            self.checkData(data)

            folder = os.path.dirname(os.path.abspath(filename))
            for answer in itertools.chain(*data.values()):
                if SpecialField.isSpecialField(answer) and (answer.isImage() or answer.isAudio()):
                    answer.scalar = os.path.join(folder, answer.scalar)

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
