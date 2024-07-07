from typing import Optional

import logging

from .events import Event, Lgc, Solution


class Simulation:
    def __init__(self, events: list[Event]) -> None:
        self.events = events
        self.choices: list[tuple[Event, Optional[int]]] = []
        self.lgc = Lgc(0, 0, 0)

    def apply_solution(self, solution: Solution) -> None:
        def get_event_choice(event: Event) -> int:
            for cur_event, choice_index in solution.choices:
                if event == cur_event:
                    return choice_index

            raise ValueError(f"Failed to find event: {event}")

        for event in self.events:
            if (
                event.required_route is not None
                and event.required_route != solution.route
            ):
                continue

            if len(event.choices) == 0:
                self.apply(event, None)
            else:
                self.apply(event, get_event_choice(event))

    def apply(self, event: Event, choice_index: Optional[int]) -> None:
        for old_event, _ in self.choices:
            if event == old_event:
                raise ValueError(
                    f"Attempted to apply an event that has already been applied: {event}"
                )

        logging.debug(f"Applying event: {(event.name, choice_index)}")
        self.choices.append((event, choice_index))

        logging.debug(
            f"  Applying completion LGC: {self.lgc.simple_str()} + {event.completion.simple_str()} = {(self.lgc + event.completion).simple_str()}"
        )
        self.lgc += event.completion
        if choice_index is not None:
            assert len(event.choices) > 0

            choice_lgc = event.choices[choice_index].impact
            logging.debug(
                f"  Applying choice {choice_index} LGC: {self.lgc.simple_str()} + {choice_lgc.simple_str()} = {(self.lgc + choice_lgc).simple_str()}"
            )
            self.lgc += choice_lgc
        else:
            assert len(event.choices) == 0
