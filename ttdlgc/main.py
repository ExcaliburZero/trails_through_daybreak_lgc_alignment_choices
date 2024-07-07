from typing import Annotated, Any, Optional

import logging
import pathlib

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
) -> int:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s> %(message)s",
    )

    with open(events_filepath, "r", encoding="utf-8") as input_stream:
        events = Event.multiple_from_csv(input_stream)

    if constraint is None:
        constraint = []

    problem = create_milp(events, constraint)
    logging.debug(problem)

    solver = pulp.PULP_CBC_CMD(msg=0)

    problem.solve(solver)
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

    if output_solution_filepath is not None:
        with open(output_solution_filepath, "w", encoding="utf8") as output_stream:
            solution.write_csv(output_stream)
        logging.info(f"Wrote generated solution to: {output_solution_filepath}")

    simulation = Simulation(events)
    simulation.apply_solution(solution)

    logging.info(f"Final LGC = {simulation.lgc}")

    return SUCCESS


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
) -> int:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s> %(message)s",
    )

    with open(events_filepath, "r", encoding="utf-8") as input_stream:
        events = Event.multiple_from_csv(input_stream)

    with open(input_solution_filepath, "r", encoding="utf8") as input_stream:
        solution = Solution.from_csv(events, input_stream)
    logging.info(f"Loaded solution from: {input_solution_filepath}")

    simulation = Simulation(events)
    simulation.apply_solution(solution)

    logging.info(f"Final LGC = {simulation.lgc}")

    return SUCCESS


def main_without_args() -> Any:
    return app()
