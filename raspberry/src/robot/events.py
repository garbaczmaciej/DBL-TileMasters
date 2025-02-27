from datetime import datetime

from .config import Config as config


class Event:
    """
    Class describing an event. It contains the time of the event.
    """
    def __init__(self, time: datetime = datetime.now()) -> None:
        self.time = time

    def __repr__(self) -> str:
        return f"Event({self.get_time_as_str()})"

    def is_ready(self) -> bool:
        """
        This method returns whether the event is ready.
        Example: event.time = 8:32; current_time = 9:02; event.time.is_ready() == True 
        """
        return datetime.now() > self.time

    def update_time(self, new_time: datetime) -> None:
        """
        Updates the time of the event to the given time.
        """
        self.time = new_time

    def get_time_as_str(self) -> str:
        return datetime.strftime(self.time, config.EVENT_TIME_STR)[:config.EVENT_TIME_STR_SPACE]


class TimeoutEvent(Event):
    """
    Class describing the timeout event. It can be used as the sleep instruction end time.
    """
    def __repr__(self) -> str:
        return f"TimeoutEvent({self.get_time_as_str()})"

    


class TileEvent(Event):
    """
    Class describing the event of a given tile being at certain place in the given time. 
    """
    def __init__(self, time: datetime, tile: int) -> None:
        super().__init__(time)
        self.tile = tile

    def __repr__(self) -> str:
        return f"TileEvent({self.get_time_as_str()}, {config.TILE_COLOR_DICT[self.tile]})"

