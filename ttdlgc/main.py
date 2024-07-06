import pathlib

import typer

from .events import Event

SUCCESS = 0
_FAILURE = 1


def main(events_filepath: pathlib.Path) -> int:
    with open(events_filepath, "r", encoding="utf-8") as input_stream:
        events = Event.multiple_from_csv(input_stream)

    print(events)

    return SUCCESS


def main_without_args() -> None:
    return typer.run(main)
