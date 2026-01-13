
from .game import GameStateModel, NobodyKnewResult
from .loader import GameStateLoader, SpecialField

from yaml import SafeLoader, SafeDumper

SafeLoader.add_constructor(u'!double', SpecialField.doubleJeopardyConstructor)
SafeLoader.add_constructor(u'!image', SpecialField.imageAnswerConstructor)
SafeLoader.add_constructor(u'!audio', SpecialField.audioAnswerConstructor)

doubleAndImageConstructor = SpecialField.makeDoubleJeopardyAndConstructor(SpecialField.imageAnswerConstructor)
SafeLoader.add_constructor(u'!double*image', doubleAndImageConstructor)

doubleAndAudioConstructor = SpecialField.makeDoubleJeopardyAndConstructor(SpecialField.audioAnswerConstructor)
SafeLoader.add_constructor(u'!double*audio', doubleAndAudioConstructor)