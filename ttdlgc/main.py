import logging
import pathlib

import typer

from .events import Event
from .milp import create_milp, extract_solution

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

    solution = extract_solution(events, problem)
    logging.info("===============")
    logging.info("Choices:")
    logging.info(f"\tChapter 5 Route: {solution.route}")
    for event, choice_index in solution.choices:
        logging.info(
            f"\t{event.name} chose <{event.choices[choice_index].name}> ({choice_index}) ({event.choices[choice_index].impact})"
        )

    return SUCCESS


def main_without_args() -> None:
    return typer.run(main)
