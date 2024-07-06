from typing import Optional

import logging

from .events import Event, Lgc


class Simulation:
    def __init__(self, events: list[Event]) -> None:
        self.events = events
        self.choices: list[tuple[Event, Optional[int]]] = []
        self.lgc = Lgc(0, 0, 0)

    def apply(self, event: Event, choice_index: Optional[int]) -> None:
        for old_event, _ in self.choices:
            if event == old_event:
                raise ValueError(
                    f"Attempted to apply an event that has already been applied: {event}"
                )

        logging.debug(f"Applying event: {(event, choice_index)}")
        self.choices.append((event, choice_index))

        logging.debug(
            f"  Applying completion LGC: {self.lgc} + {event.completion} = {self.lgc + event.completion}"
        )
        self.lgc += event.completion
        if choice_index is not None:
            assert len(event.choices) > 0

            choice_lgc = event.choices[choice_index].impact
            logging.debug(
                f"  Applying choice {choice_index} LGC: {self.lgc} + {choice_lgc} = {self.lgc + choice_lgc}"
            )
            self.lgc += choice_lgc
        else:
            assert len(event.choices) == 0
