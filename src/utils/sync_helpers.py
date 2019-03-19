from datetime import datetime
from threading import Event
from typing import List


def wait_for_all_events(events: List[Event], timeout: float) -> bool:
    starting_time = datetime.now()
    for event in events:
        current_time = datetime.now()
        real_timeout = timeout - (current_time - starting_time).total_seconds()

        if real_timeout > 0:
            is_set = event.wait(timeout)
            if not is_set:
                return False
        else:
            return False
    return True
