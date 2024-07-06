from dataclasses import dataclass
from typing import Callable, IO, Optional

import csv
import enum

CHAPTER = "Chapter"
DATE = "Date"
NAME = "Name"
COMPLETION_LAW = "Completion L"
COMPLETION_GREY = "Completion G"
COMPLETION_CHAOS = "Completion C"
ROUTE = "Route"
CHOICE_N: Callable[[int], str] = lambda n: f"Choice {n}"
CHOICE_N_L: Callable[[int], str] = lambda n: f"Choice {n} L"
CHOICE_N_G: Callable[[int], str] = lambda n: f"Choice {n} G"
CHOICE_N_C: Callable[[int], str] = lambda n: f"Choice {n} C"


@dataclass(frozen=True)
class Lgc:
    law: int
    grey: int
    chaos: int

    def __add__(self, other: "Lgc") -> "Lgc":
        return Lgc(
            law=self.law + other.law,
            grey=self.grey + other.grey,
            chaos=self.chaos + other.chaos,
        )

    def simple_str(self) -> str:
        return f"Lgc({self.law}, {self.grey}, {self.chaos})"


@dataclass(frozen=True)
class Choice:
    name: str
    impact: Lgc


class TtdMonth(enum.Enum):
    September = 9
    October = 10
    November = 11
    December = 12

    @staticmethod
    def from_str(string: str) -> "TtdMonth":
        return TtdMonth[string]


@dataclass(frozen=True, order=True)
class TtdDate:
    month: TtdMonth
    day: int

    @staticmethod
    def from_str(string: str) -> "TtdDate":
        parts = string.split(" ")
        assert len(parts) == 2

        return TtdDate(month=TtdMonth.from_str(parts[0]), day=int(parts[1]))


class Route(enum.Enum):
    Law = enum.auto()
    Grey = enum.auto()
    Chaos = enum.auto()
    Fourth = enum.auto()

    @staticmethod
    def from_str(string: str) -> "Route":
        return Route[string]


@dataclass(frozen=True)
class Event:
    chapter: int
    date: TtdDate
    name: str
    completion: Lgc
    required_route: Optional[Route]
    choices: list[Choice]

    @staticmethod
    def multiple_from_csv(input_stream: IO[str]) -> list["Event"]:
        events: list["Event"] = []

        for row in csv.DictReader(input_stream):
            if row[CHAPTER] == "":
                # Skip empty rows
                continue

            chapter = int(row[CHAPTER])
            date = TtdDate.from_str(row[DATE])
            name = row[NAME]
            completion = Lgc(
                law=int(row[COMPLETION_LAW]),
                grey=int(row[COMPLETION_GREY]),
                chaos=int(row[COMPLETION_CHAOS]),
            )
            required_route = Route.from_str(row[ROUTE]) if row[ROUTE] != "" else None

            choices = []
            for i in range(1, 4):
                choice_name = row[CHOICE_N(i)]
                if choice_name == "":
                    continue

                choice = Choice(
                    name=choice_name,
                    impact=Lgc(
                        law=int(row[CHOICE_N_L(i)]),
                        grey=int(row[CHOICE_N_G(i)]),
                        chaos=int(row[CHOICE_N_C(i)]),
                    ),
                )
                choices.append(choice)

            events.append(
                Event(
                    chapter=chapter,
                    date=date,
                    name=name,
                    completion=completion,
                    required_route=required_route,
                    choices=choices,
                )
            )

        return events
