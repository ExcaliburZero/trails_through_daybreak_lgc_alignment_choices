from typing import Iterable, Optional

import collections
import enum

import pulp

from .events import Event, Route, Solution


LAST_CHAPTER = 7

LAW_LEVEL_3 = 60
GREY_LEVEL_3 = 50
CHAOS_LEVEL_3 = 30

LAW_LEVEL_4 = 90
GREY_LEVEL_4 = 75
CHAOS_LEVEL_4 = 45

LAW_LEVEL_5 = 120
GREY_LEVEL_5 = 100
CHAOS_LEVEL_5 = 75

ImpactsDict = dict[
    int,
    list[
        tuple[Optional[pulp.LpVariable], int]
        | tuple[Optional[pulp.LpVariable], pulp.LpVariable, int]
    ],
]


class Constraint(enum.Enum):
    LawLv4AtEnd = "LawLv4AtEnd"
    GreyLv4AtEnd = "GreyLv4AtEnd"
    ChaosLv4AtEnd = "ChaosLv4AtEnd"
    LawLv5AtEnd = "LawLv5AtEnd"
    GreyLv5AtEnd = "GreyLv5AtEnd"
    ChaosLv5AtEnd = "ChaosLv5AtEnd"


class Goal(enum.Enum):
    MaximizeLaw = "MaximizeLaw"
    MaximizeGrey = "MaximizeGrey"
    MaximizeChaos = "MaximizeChaos"


def extract_solution(events: list[Event], problem: pulp.LpProblem) -> Solution:
    variables = problem.variablesDict()

    route = None
    if variables["chapter_5_route_law"].varValue > 0:
        route = Route.Law
    elif variables["chapter_5_route_grey"].varValue > 0:
        route = Route.Grey
    elif variables["chapter_5_route_chaos"].varValue > 0:
        route = Route.Chaos
    elif variables["chapter_5_route_fourth"].varValue > 0:
        route = Route.Fourth

    assert route is not None

    choices = []
    for i, event in enumerate(events):
        if event.required_route is not None and event.required_route != route:
            continue

        if len(event.choices) > 0:
            for o in range(0, len(event.choices)):

                value = variables[f"event_{i}_option_{o}"]
                if value.varValue > 0:
                    choices.append((event, o))
                    break

    return Solution(choices=choices, route=route)


def create_milp(
    events: list[Event], constraints: Iterable[Constraint], goal: Optional[Goal]
) -> pulp.LpProblem:
    problem = pulp.LpProblem("LGC_Alignment", pulp.LpMaximize)

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

    law_chapter_impacts: ImpactsDict = collections.defaultdict(lambda: [])
    grey_chapter_impacts: ImpactsDict = collections.defaultdict(lambda: [])
    chaos_chapter_impacts: ImpactsDict = collections.defaultdict(lambda: [])

    # Objective function
    if goal is None:
        problem += 0 == 0, "No goal"
    elif goal == Goal.MaximizeLaw:
        problem += law_chapter_variables[-1], "Maximize law alignment"
    elif goal == Goal.MaximizeGrey:
        problem += grey_chapter_variables[-1], "Maximize grey alignment"
    elif goal == Goal.MaximizeChaos:
        problem += chaos_chapter_variables[-1], "Maximize chaos alignment"

    # Chapter 5 route
    law_route = pulp.LpVariable("chapter_5_route_law", cat=pulp.const.LpBinary)
    grey_route = pulp.LpVariable("chapter_5_route_grey", cat=pulp.const.LpBinary)
    chaos_route = pulp.LpVariable("chapter_5_route_chaos", cat=pulp.const.LpBinary)
    fourth_route = pulp.LpVariable("chapter_5_route_fourth", cat=pulp.const.LpBinary)

    problem += (
        law_route + grey_route + chaos_route + fourth_route == 1,
        "Must do one and only one route during chapter 5",
    )

    # Encode event choices
    event_choices = {}
    for i, event in enumerate(events):
        route_variable = None
        if event.required_route == Route.Law:
            route_variable = law_route
        elif event.required_route == Route.Grey:
            route_variable = grey_route
        elif event.required_route == Route.Chaos:
            route_variable = chaos_route
        elif event.required_route == Route.Fourth:
            route_variable = fourth_route

        for j in range(event.chapter, LAST_CHAPTER + 1):
            law_chapter_impacts[j].append((route_variable, event.completion.law))
            grey_chapter_impacts[j].append((route_variable, event.completion.grey))
            chaos_chapter_impacts[j].append((route_variable, event.completion.chaos))

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
                    law_chapter_impacts[j].append(
                        (route_variable, option, event.choices[o].impact.law)
                    )
                    grey_chapter_impacts[j].append(
                        (route_variable, option, event.choices[o].impact.grey)
                    )
                    chaos_chapter_impacts[j].append(
                        (route_variable, option, event.choices[o].impact.chaos)
                    )

    # Encode requirements to start routes at chapter 5
    # TODO: Model fourth route requirement
    # TODO: Account for default route if alignment score is too low?
    problem += (
        law_route * LAW_LEVEL_3 <= law_chapter_variables[4],
        "Law route alignment requirement",
    )
    problem += (
        grey_route * GREY_LEVEL_3 <= grey_chapter_variables[4],
        "Grey route alignment requirement",
    )
    problem += (
        chaos_route * CHAOS_LEVEL_3 <= chaos_chapter_variables[4],
        "Chaos route alignment requirement",
    )

    # TODO: actually model the fourth route constraint instead
    problem += fourth_route == 0, "Not modelling the fourth route for now..."

    # Encode alignment impacts
    for alignment_name, variables, impact_set in [
        ("Law", law_chapter_variables, law_chapter_impacts),
        ("Grey", grey_chapter_variables, grey_chapter_impacts),
        ("Chaos", chaos_chapter_variables, chaos_chapter_impacts),
    ]:
        for chapter, impacts in impact_set.items():
            variable = variables[chapter - 1]

            expression = 0
            for j, impact in enumerate(impacts):
                if len(impact) == 2:
                    required_route, effect = impact

                    if required_route is None:
                        expression += effect
                    else:
                        expression += required_route * effect
                elif len(impact) == 3:
                    required_route, option, effect = impact

                    if required_route is None:
                        expression += option * effect
                    else:
                        # Would be `required_route * option * effect`, but we need to keep it linear
                        # https://or.stackexchange.com/questions/37/how-to-linearize-the-product-of-two-binary-variables
                        variable_both = pulp.LpVariable(
                            f"route_and_option_{alignment_name}_{chapter}_{j}",
                            cat=pulp.const.LpBinary,
                        )
                        problem.addVariable(variable_both)

                        problem += variable_both <= required_route
                        problem += variable_both <= option
                        problem += variable_both >= required_route + option - 1

                        expression += variable_both * effect

            problem += (
                variable == expression,
                f"{alignment_name} value at end of chapter {chapter}",
            )

    # User-provided constraints
    for constraint in constraints:
        if constraint == Constraint.LawLv4AtEnd:
            problem += law_chapter_variables[-1] >= LAW_LEVEL_4
        elif constraint == Constraint.GreyLv4AtEnd:
            problem += grey_chapter_variables[-1] >= GREY_LEVEL_4
        elif constraint == Constraint.ChaosLv4AtEnd:
            problem += chaos_chapter_variables[-1] >= CHAOS_LEVEL_4
        elif constraint == Constraint.LawLv5AtEnd:
            problem += law_chapter_variables[-1] >= LAW_LEVEL_5
        elif constraint == Constraint.GreyLv5AtEnd:
            problem += grey_chapter_variables[-1] >= GREY_LEVEL_5
        elif constraint == Constraint.ChaosLv5AtEnd:
            problem += chaos_chapter_variables[-1] >= CHAOS_LEVEL_5

    return problem
