import logging
import pathlib

import typer

from .events import Event
from .milp import create_milp

SUCCESS = 0
_FAILURE = 1


def main(events_filepath: pathlib.Path) -> int:
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s> %(message)s")

    with open(events_filepath, "r", encoding="utf-8") as input_stream:
        events = Event.multiple_from_csv(input_stream)

    problem = create_milp(events)
    logging.info(problem)

    problem.solve()
    logging.info("==============")
    logging.info("Solution:")
    for vairable in problem.variables():
        logging.info(f"{vairable} = {vairable.varValue}")

    return SUCCESS


def main_without_args() -> None:
    return typer.run(main)
