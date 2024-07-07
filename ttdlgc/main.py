import logging
import pathlib

import typer

from .events import Event
from .milp import create_milp, extract_solution
from .simulation import Simulation

SUCCESS = 0
_FAILURE = 1


def main(
    events_filepath: pathlib.Path,
    output_solution_filepath: pathlib.Path,
    verbose: bool = False,
) -> int:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s> %(message)s",
    )

    with open(events_filepath, "r", encoding="utf-8") as input_stream:
        events = Event.multiple_from_csv(input_stream)

    problem = create_milp(events)
    logging.debug(problem)

    problem.solve()
    logging.debug("==============")
    logging.debug("Solution:")
    for vairable in problem.variables():
        logging.debug(f"{vairable} = {vairable.varValue}")

    solution = extract_solution(events, problem)
    logging.info("===============")
    logging.info("Choices:")
    logging.info(f"\tChapter 5 Route: {solution.route}")
    for event, choice_index in solution.choices:
        logging.info(
            f"\t{event.name} chose <{event.choices[choice_index].name}> ({choice_index}) ({event.choices[choice_index].impact})"
        )

    with open(output_solution_filepath, "w", encoding="utf8") as output_stream:
        solution.write_csv(output_stream)
    logging.info(f"Wrote generated solution to: {output_solution_filepath}")

    simulation = Simulation(events)
    simulation.apply_solution(solution)

    logging.info(f"Final LGC = {simulation.lgc}")

    return SUCCESS


def main_without_args() -> None:
    return typer.run(main)
