from dataclasses import dataclass


@dataclass(frozen=True)
class Lgc:
    law: int
    grey: int
    chaos: int


@dataclass(frozen=True)
class Choice:
    name: str
    impact: Lgc


@dataclass(frozen=True)
class Event:
    chapter: int
    name: str
    completion: Lgc
    choices: list[Choice]
