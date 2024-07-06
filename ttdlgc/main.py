import logging
import pathlib

import typer

from .events import Event
from .simulation import Simulation

SUCCESS = 0
_FAILURE = 1


def main(events_filepath: pathlib.Path) -> int:
    logging.getLogger().setLevel(logging.DEBUG)

    with open(events_filepath, "r", encoding="utf-8") as input_stream:
        events = Event.multiple_from_csv(input_stream)

    simulation = Simulation(events=events)

    for event in events:
        logging.debug("--------")
        if len(event.choices) == 0:
            simulation.apply(event, None)
        else:
            simulation.apply(event, 0)

    return SUCCESS


def main_without_args() -> None:
    return typer.run(main)
