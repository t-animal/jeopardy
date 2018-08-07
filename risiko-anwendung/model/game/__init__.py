
from .game import GameStateModel
from .loader import GameStateLoader, SpecialField

from yaml import SafeLoader, SafeDumper

SafeLoader.add_constructor(u'!double', SpecialField.doubleJeopardyConstructor)
SafeLoader.add_constructor(u'!image', SpecialField.imageAnswerConstructor)