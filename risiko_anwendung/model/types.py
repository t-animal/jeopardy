from __future__ import annotations

from collections import OrderedDict
from typing import TYPE_CHECKING, TypeAlias, TypedDict

if TYPE_CHECKING:
    from risiko_anwendung.model.game.game import NobodyKnewResult, Result
    from risiko_anwendung.model.game.loader import SpecialField
else:
    class Result: ...
    class NobodyKnewResult: ...
    class SpecialField: ...


PlayerKey: TypeAlias = str
CategoryName: TypeAlias = str
RowIndex: TypeAlias = int
ColumnIndex: TypeAlias = int
GridIndex: TypeAlias = tuple[RowIndex, ColumnIndex]

AnswerValue: TypeAlias = str | SpecialField
CategoryAnswers: TypeAlias = list[AnswerValue]
GameTable: TypeAlias = OrderedDict[CategoryName, CategoryAnswers]

ResultLike: TypeAlias = Result | NobodyKnewResult
ResultByAnswer: TypeAlias = list[ResultLike]
ResultsByRow: TypeAlias = list[ResultByAnswer]
ResultsByCategory: TypeAlias = dict[CategoryName, ResultsByRow]


class SerializedPlayer(TypedDict):
    key: PlayerKey
    name: str


class SerializedScoredResult(TypedDict):
    player: PlayerKey
    correct: bool
    wager: int


SerializedResultEntry: TypeAlias = SerializedScoredResult | NobodyKnewResult
SerializedResultsByIndex: TypeAlias = dict[str, list[SerializedResultEntry]]


class PersistedState(TypedDict, total=False):
    players: list[SerializedPlayer]
    results: SerializedResultsByIndex
