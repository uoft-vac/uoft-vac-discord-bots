'''MeetingTime class
Author: Sunny Lin
Editors: 
Last modified: Apr 7, 26
'''
from datetime import datetime, timezone


class MeetingTime:
    '''
    Stores all relevant fields for a meeting time,
    as well as its UNIX timestamp equivalent.
    '''
    _year: int
    _month: int
    _day: int
    _hour: int
    _minute: int

    _timestamp: float

    def __init__(self, timestamp: float) -> None:
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)

        self._year = dt.year
        self._month = dt.month
        self._day = dt.day
        self._hour = dt.hour
        self._minute = dt.minute
    
    # Inits:
    @classmethod
    def from_fields(cls, year: int, month: int, day: int, hour: int, minute: int):
        return cls(datetime(year, month, day, hour, minute, tzinfo=timezone.utc).timestamp())
    
    @classmethod
    def from_timestamp(cls, timestamp: float):
        return cls(timestamp)
    
    # Getters:
    def get_year(self) -> int: return self._year
    def get_month(self) -> int: return self._month
    def get_day(self) -> int: return self._day
    def get_hour(self) -> int: return self._hour
    def get_minute(self) -> int: return self._minute
    def get_timestamp(self) -> float: return self._timestamp
