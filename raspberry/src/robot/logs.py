from datetime import datetime
from abc import ABC, abstractmethod


from .config import Config as config
from .utils import Utils as utils


# This is used for a log id. It is increased by 1 every time the Log class is made.
LOG_COUNTER = 1


class Log:
    """
    A class representing a log object.
    """
    def __init__(self, component_name: str, _type: str, description: str, time: datetime, additional_data: dict = dict()) -> None:
        # Id of the log
        self.id = self._get_id()
        # Name of the component that created that log
        self.component_name = component_name
        # Type of the log: for now it can be either "error" or "action"
        self.type = _type
        # Description of the log
        self.description = description
        # Time of the log
        self.time = time
        # Additional data
        self.additional_data = additional_data

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "componentName": self.component_name,
            "type": self.type,
            "description": self.description,
            "additionalData": self.additional_data,
            "date": self.time.strftime(config.LOG_DATE_STR_FORMAT),
            "time": self.time.strftime(config.LOG_TIME_STR_FORMAT)
        }

    def __str__(self) -> str:
        """
        This returns the string representation of an object.
        """
        # Its in the utils.py!
        return utils.get_log_format_str(self.id, self.get_date_as_str(), self.component_name, self.description)

    def get_date_as_str(self) -> str:
        """
        Returns the log date as a string.
        """
        return datetime.strftime(self.time, config.LOG_DATETIME_STR)[:config.LOG_TIME_SPACE]

    @classmethod
    def _get_id(cls) -> None:
        """
        Returns the id of the log. Everytime this method is called it increases the counter by 1.
        """
        global LOG_COUNTER

        id = LOG_COUNTER
        LOG_COUNTER += 1
        
        return id


class Logs:
    """
    Logs representation, which holds the info about actions and errors that occured in components.
    """

    TILE_TO_COUNT_FORMAT = {
        config.BLACK_TILE: "b",
        config.WHITE_TILE: "w",
        config.UNDEFINED_TILE: "u"
    }

    def __init__(self) -> None:
        # List of logs.
        self._logs: list[Log] = list()
        # This is used so that the header is printed the first time a log is printed.
        self.header_printed = False

        self.tile_count = {
            "b": 0,
            "w": 0,
            "u": 0,
            "p": 0
        }

    def __str__(self) -> str:
        return self._get_header() + "\n" + "\n".join([str(log) for log in self._logs])

    def report_tile(self, tile: int) -> None:
        self.tile_count[self.TILE_TO_COUNT_FORMAT[tile]] += 1
    
    def report_push_tile(self) -> None:
        self.tile_count["p"] += 1

    def to_jsonify_format(self, last_log_id: int = 0) -> list:
        logs = self.get_logs_since(last_log_id)
            
        return [log.to_dict() for log in logs]

    def get_logs_since(self, last_log_id: int = 0) -> list:
        """
        Gets logs since the log with the given id.
        """
        if not self._logs:
            return self._logs
        
        if last_log_id == 0:
            return self._logs[-config.GET_LOGS_DEFAULT_AMOUNT:]

        last_local_log_id = self._logs[-1].id

        diff = last_log_id - last_local_log_id

        if diff >= 0:
            return []
        
        return self._logs[diff:]

    def print(self, amount: int = 0) -> None:
        """
        Prints the logs. If given the amount, it will print last amount of logs.
        If amount is 0, it will print all of the logs.
        """
        print(self)

    def _get_header(self) -> str:
        header = utils.get_log_format_str("ID", "HH:MM:SS:mmm", "COMPONENT_NAME", "DESCRIPTION")
        return header

    def print_header(self) -> None:
        """
        Prints the log header.
        """
        print(self._get_header())

    def add(self, log: Log) -> None:
        """
        Adds a given log to the internal logs.
        """
        # If the logs should be used:
        if config.USE_LOGS:

            # Add the log to the internal logs
            self._logs.append(log)

            # If the logs should be printed
            if config.PRINT_LOGS:
                if not self.header_printed:
                    self.print_header()
                    self.header_printed = True
                # Print the logs.
                print(log)

    def add_multiple(self, logs: list[Log]) -> None:
        """
        Add multiple logs to the internal logs.
        """
        for log in logs:
            self.add_log(log)


class LogComponent(ABC):
    """
    Abstract class for a component that can log its actions.
    """

    def __init__(self, logs: Logs) -> None:
        self.logs = logs

    @property
    @abstractmethod
    def COMPONENT_NAME(self) -> str:
        """
        This should return the component name.
        """
        pass

    def add_log(self, _type: str, description: str) -> None:
        """
        Saves the log of given type, description and current time.
        """
        # Create a log object.
        log = Log(
            self.COMPONENT_NAME,
            _type,
            description,
            datetime.now()
        )
        # Save the log object.
        self.logs.add(log)