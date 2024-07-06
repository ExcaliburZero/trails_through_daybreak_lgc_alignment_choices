import collections
import logging
import pathlib

import pulp
import typer

from .events import Event

SUCCESS = 0
_FAILURE = 1

LAST_CHAPTER = 7


def main(events_filepath: pathlib.Path) -> int:
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s> %(message)s")

    with open(events_filepath, "r", encoding="utf-8") as input_stream:
        events = Event.multiple_from_csv(input_stream)

    # TODO: remove
    events = [event for event in events if len(event.choices) <= 2]

    problem = create_milp(events)
    logging.info(problem)

    problem.solve()
    logging.info("==============")
    logging.info("Solution:")
    for vairable in problem.variables():
        logging.info(f"{vairable} = {vairable.varValue}")

    return SUCCESS


def create_milp(events: list[Event]) -> pulp.LpProblem:
    problem = pulp.LpProblem()

    # Objective function
    problem += 0, "objective"

    law_chapter_impacts: dict[int, list[int | tuple[pulp.LpVariable, int]]] = (
        collections.defaultdict(lambda: [])
    )

    # Encode event choices
    event_choices = {}
    for i, event in enumerate(events):
        for j in range(event.chapter, LAST_CHAPTER + 1):
            law_chapter_impacts[j].append(event.completion.law)

        if len(event.choices) > 0:
            option_1 = pulp.LpVariable(
                f"event_{i}_option_1",
                0,
                len(event.choices) - 1,
                cat=pulp.const.LpInteger,
            )
            option_2 = pulp.LpVariable(
                f"event_{i}_option_2",
                0,
                len(event.choices) - 1,
                cat=pulp.const.LpInteger,
            )
            problem.addVariable(option_1)
            problem.addVariable(option_2)
            event_choices[i] = (option_1, option_2)

            problem += option_1 + option_2 == 1, f"Pick one option for event {i}"

            for j in range(event.chapter, LAST_CHAPTER + 1):
                law_chapter_impacts[j].append((option_1, event.choices[0].impact.law))
                law_chapter_impacts[j].append((option_2, event.choices[1].impact.law))

    # Encode alignment impacts
    for chapter, law_impacts in law_chapter_impacts.items():
        variable = pulp.LpVariable(
            f"law_at_chapter_{chapter}_end", cat=pulp.const.LpInteger
        )
        problem.addVariable(variable)

        problem += (
            variable
            == sum(
                [
                    impact if isinstance(impact, int) else (impact[0] * impact[1])
                    for impact in law_impacts
                ]
            ),
            f"Law value at end of chapter {chapter}",
        )

    return problem


def main_without_args() -> None:
    return typer.run(main)
