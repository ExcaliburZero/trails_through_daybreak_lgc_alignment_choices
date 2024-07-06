import collections

import pulp

from .events import Event


LAST_CHAPTER = 7


def create_milp(events: list[Event]) -> pulp.LpProblem:
    problem = pulp.LpProblem("LGC Alignment", pulp.LpMaximize)

    # Create alignment variables
    law_chapter_variables = [
        pulp.LpVariable(f"law_at_chapter_{chapter}_end", cat=pulp.const.LpInteger)
        for chapter in range(1, LAST_CHAPTER + 1)
    ]
    grey_chapter_variables = [
        pulp.LpVariable(f"grey_at_chapter_{chapter}_end", cat=pulp.const.LpInteger)
        for chapter in range(1, LAST_CHAPTER + 1)
    ]
    chaos_chapter_variables = [
        pulp.LpVariable(f"chaos_at_chapter_{chapter}_end", cat=pulp.const.LpInteger)
        for chapter in range(1, LAST_CHAPTER + 1)
    ]

    law_chapter_impacts: dict[int, list[int | tuple[pulp.LpVariable, int]]] = (
        collections.defaultdict(lambda: [])
    )
    grey_chapter_impacts: dict[int, list[int | tuple[pulp.LpVariable, int]]] = (
        collections.defaultdict(lambda: [])
    )
    chaos_chapter_impacts: dict[int, list[int | tuple[pulp.LpVariable, int]]] = (
        collections.defaultdict(lambda: [])
    )

    # Objective function
    problem += law_chapter_variables[-1], "Maximize law alignment"

    # Encode event choices
    event_choices = {}
    for i, event in enumerate(events):
        for j in range(event.chapter, LAST_CHAPTER + 1):
            law_chapter_impacts[j].append(event.completion.law)
            grey_chapter_impacts[j].append(event.completion.grey)
            chaos_chapter_impacts[j].append(event.completion.chaos)

        if len(event.choices) > 0:
            option_variables = []
            for o in range(0, len(event.choices)):
                option = pulp.LpVariable(
                    f"event_{i}_option_{o}",
                    0,
                    1,
                    cat=pulp.const.LpInteger,
                )
                problem.addVariable(option)
                option_variables.append(option)

            event_choices[i] = option_variables

            problem += sum(option_variables) == 1, f"Pick one option for event {i}"

            for j in range(event.chapter, LAST_CHAPTER + 1):
                for o, option in enumerate(option_variables):
                    law_chapter_impacts[j].append((option, event.choices[o].impact.law))
                    grey_chapter_impacts[j].append(
                        (option, event.choices[o].impact.grey)
                    )
                    chaos_chapter_impacts[j].append(
                        (option, event.choices[o].impact.chaos)
                    )

    # Encode alignment impacts
    for alignment_name, variables, impact_set in [
        ("Law", law_chapter_variables, law_chapter_impacts),
        ("Grey", grey_chapter_variables, grey_chapter_impacts),
        ("Choas", chaos_chapter_variables, chaos_chapter_impacts),
    ]:
        for chapter, impacts in impact_set.items():
            variable = variables[chapter - 1]

            problem += (
                variable
                == sum(
                    [
                        impact if isinstance(impact, int) else (impact[0] * impact[1])
                        for impact in impacts
                    ]
                ),
                f"{alignment_name} value at end of chapter {chapter}",
            )

    return problem
