from typing import Annotated, Any, Optional

import logging
import pathlib
import sys

import pulp
import typer

from .events import Event, Solution
from .milp import create_milp, extract_solution, Constraint
from .simulation import Simulation

SUCCESS = 0
_FAILURE = 1

app = typer.Typer()


@app.command()
def solve(
    events_filepath: Annotated[
        pathlib.Path,
        typer.Option(help="Filepath to CSV file containing event information."),
    ],
    output_solution_filepath: Annotated[
        Optional[pathlib.Path],
        typer.Option(help="Filepath to write the generated choices to."),
    ] = None,
    constraint: Annotated[
        Optional[list[Constraint]], typer.Option(help="Constraints to add to the MILP.")
    ] = None,
    verbose: bool = False,
) -> None:
    failed = False

    logger = create_logger(verbose)

    with open(events_filepath, "r", encoding="utf-8") as input_stream:
        events = Event.multiple_from_csv(input_stream)

    if constraint is None:
        constraint = []

    problem = create_milp(events, constraint)
    logger.debug(problem)

    solver = pulp.PULP_CBC_CMD(msg=0)

    problem.solve(solver)
    logger.debug("==============")
    logger.debug("Solution:")
    for vairable in problem.variables():
        logger.debug(f"{vairable} = {vairable.varValue}")

    if problem.status < 0:
        logger.error("Failed to create a solution that satisfies all constraints.")
        logger.error("The following is the solver's best attempt solution.")

        failed = True
    else:
        logger.info("Generated a valid solution.")

    solution = extract_solution(events, problem)
    logger.info("===============")
    logger.info("Choices:")
    logger.info(f"\tChapter 5 Route: {solution.route}")
    for event, choice_index in solution.choices:
        logger.info(
            f"\t{event.name} chose <{event.choices[choice_index].name}> ({choice_index}) ({event.choices[choice_index].impact})"
        )

    if output_solution_filepath is not None:
        with open(output_solution_filepath, "w", encoding="utf8") as output_stream:
            solution.write_csv(output_stream)
        logger.info(f"Wrote generated solution to: {output_solution_filepath}")

    simulation = Simulation(events)
    simulation.apply_solution(solution)

    logger.info(f"Final LGC = {simulation.lgc}")

    if failed:
        sys.exit(1)


@app.command()
def simulate(
    events_filepath: Annotated[
        pathlib.Path,
        typer.Option(help="Filepath to CSV file containing event information."),
    ],
    input_solution_filepath: Annotated[
        pathlib.Path,
        typer.Option(help="Filepath to CSV file of choices to load as input."),
    ],
    verbose: bool = False,
) -> None:
    logger = create_logger(verbose)

    with open(events_filepath, "r", encoding="utf-8") as input_stream:
        events = Event.multiple_from_csv(input_stream)

    with open(input_solution_filepath, "r", encoding="utf8") as input_stream:
        solution = Solution.from_csv(events, input_stream)
    logger.info(f"Loaded solution from: {input_solution_filepath}")

    simulation = Simulation(events)
    simulation.apply_solution(solution)

    logger.info(f"Final LGC = {simulation.lgc}")


def create_logger(verbose: bool) -> logging.Logger:
    logger = logging.getLogger("ttdlgc_model")
    logger.setLevel(logging.DEBUG)

    logger.propagate = False

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if verbose else logging.INFO)

    ch.setFormatter(CustomFormatter())

    logger.addHandler(ch)

    return logger


class CustomFormatter(logging.Formatter):
    # https://stackoverflow.com/a/56944256/4764550
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    fmt = "%(levelname)s> %(message)s"

    FORMATS = {
        logging.DEBUG: grey + fmt + reset,
        logging.INFO: grey + fmt + reset,
        logging.WARNING: yellow + fmt + reset,
        logging.ERROR: red + fmt + reset,
        logging.CRITICAL: bold_red + fmt + reset,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def main_without_args() -> Any:
    return app()
