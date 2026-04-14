'''MeetingTime class
Author: Sunny Lin
Editors: 
Last modified: Apr 7, 26
'''
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo
from time import time

from common_bot_helper import parse_input

TORONTO_TIMEZONE = ZoneInfo("America/Toronto")


# HELPER FUNCTIONS

'''
Arg validating functions:
Returns the value to initialise the MeetingTime object (int) if valid.
Returns None if invalid.

For from_input init function.
'''

MONTHS = (
    'january', 'jan',
    'february', 'feb',
    'march', 'mar',
    'april', 'apr',
    'may', None,
    'june', 'jun',
    'july', 'jul',
    'august', 'aug',
    'september', 'sep',
    'october', 'oct',
    'november', 'nov',
    'december', 'dec',
)
MONTH_LAST_DAYS = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

def _validate_year(arg: str) -> int | None:
    if arg.isdigit(): return int(arg)

def _validate_month(arg: str) -> int | None:
    if arg.isdigit() and 1 <= int(arg) <= 12: return int(arg)
    if arg in MONTHS: return (MONTHS.index(arg) // 2) + 1

def _validate_day(arg: str, month_i: int | None) -> int | None:
    if \
        month_i != None and \
        arg.isdigit() and \
        1 <= int(arg) <= MONTH_LAST_DAYS[month_i] \
    : return int(arg)

def _validate_hour(arg: str) -> int | None:
    if arg.isdigit() and 0 <= int(arg) <= 23: return int(arg)

def _validate_minute(arg: str) -> int | None:
    if arg.isdigit() and 0 <= int(arg) <= 59: return int(arg)


TIME_BREAKPOINTS_RE = '[ ,:-]'

class MeetingTime:
    '''
    Stores all relevant args for a meeting time,
    as well as its UNIX timestamp equivalent.

    Default init: timestamp
    '''
    _year: int
    _month: int
    _day: int
    _hour: int
    _minute: int

    _timestamp: float

    def __init__(self, timestamp: float) -> None:
        dt = datetime.fromtimestamp(timestamp, tz=TORONTO_TIMEZONE)

        self._year = dt.year
        self._month = dt.month
        self._day = dt.day
        self._hour = dt.hour
        self._minute = dt.minute

        self._timestamp = timestamp
    

    # INITS

    @classmethod
    def from_args(cls, year: int, month: int, day: int, hour: int, minute: int) -> MeetingTime:
        return cls(datetime(year, month, day, hour, minute, tzinfo=TORONTO_TIMEZONE).timestamp())
    
    @classmethod
    def from_input(cls, input: str) -> MeetingTime | str:
        args = parse_input(input, TIME_BREAKPOINTS_RE)

        # Year, month, day, hour, minute.
        init_args = [None, None, None, None, None]

        # Full input.
        if len(args) == 5:
            init_args[1] = _validate_month(args[1])
            init_args[0], init_args[2], init_args[3], init_args[4] = \
                _validate_year(args[0]), \
                _validate_day(args[2], init_args[1] - 1), \
                _validate_hour(args[3]), \
                _validate_minute(args[4])
        
        # If any args are None, the input was invalid.
        if None in init_args: return 'Invalid time input.'
        
        return cls(datetime(*init_args, tzinfo=TORONTO_TIMEZONE).timestamp())
    
    @classmethod
    def get_now(cls) -> MeetingTime: return cls(time())


    # INSTANCE METHODS

    def to_discord(self, relative: bool = False) -> str:
        return f'<t:{int(self.get_timestamp())}:{'F' if not relative else 'R'}>'


    def is_within_timeframe(self, other: MeetingTime | int, timeframe_secs: int) -> bool:
        return (self - other).get_timestamp() <= timeframe_secs


    # OPERATIONS

    def __add__(self, other: MeetingTime | int) -> MeetingTime:
        if isinstance(other, MeetingTime):
            return MeetingTime(self.get_timestamp() + other.get_timestamp())
        
        if isinstance(other, int):
            return MeetingTime(self.get_timestamp() + other)
        
        return NotImplemented

    def __sub__(self, other: MeetingTime | int) -> MeetingTime:
        return self + (-other)

    def __neg__(self) -> MeetingTime:
        return MeetingTime(-self.get_timestamp())


    # GETTERS
    def get_year(self) -> int: return self._year
    def get_month(self) -> int: return self._month
    def get_day(self) -> int: return self._day
    def get_hour(self) -> int: return self._hour
    def get_minute(self) -> int: return self._minute
    def get_timestamp(self) -> float: return self._timestamp


if __name__ == '__main__':
    from doctest import testmod
    testmod()
