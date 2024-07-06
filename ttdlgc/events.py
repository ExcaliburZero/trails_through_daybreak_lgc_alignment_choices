from dataclasses import dataclass
from typing import IO

import csv


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

    @staticmethod
    def multiple_from_csv(input_stream: IO[str]) -> list["Event"]:
        events: list["Event"] = []

        for row in csv.DictReader(input_stream):
            print(row)

        return events
