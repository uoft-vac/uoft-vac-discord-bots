'''Frodo Meet - Data
'''
from pathlib import Path

from common.util import read_json_file, write_json_file

from meeting import (Meeting,
    ATTRIBUTE_TITLE,
    ATTRIBUTE_TIME,
    ATTRIBUTE_DESCRIPTION,
    ATTRIBUTE_PARTICIPANTS,
    ATTRIBUTE_DM,
    ATTRIBUTE_RECURRENCE,
    ATTRIBUTE_ACTIVE,
    ATTRIBUTE_SOON,
)


DATA_FILE_PATH = Path(__file__).resolve().parent / 'meetings_data.json'
MEETINGS_FILE_KEY = 'meetings'

_meetings: list[Meeting] = [] # Persistent meetings list.


# DATA ACCESS FUNCTIONS

def load_meetings() -> None:
    global _meetings
    _meetings = read_meetings_from_data(read_json_file(DATA_FILE_PATH))

def get_meetings() -> list[Meeting]: return _meetings

def save_meetings() -> None:
    write_json_file(DATA_FILE_PATH, {MEETINGS_FILE_KEY: [{
        ATTRIBUTE_TITLE: meeting.get_title(),
        ATTRIBUTE_TIME: meeting.get_time().get_timestamp(),
        ATTRIBUTE_DESCRIPTION: meeting.get_description(),
        ATTRIBUTE_PARTICIPANTS: meeting.get_participants(),
        ATTRIBUTE_DM: meeting.get_dm(),
        ATTRIBUTE_RECURRENCE: meeting.get_recurrence(),
        ATTRIBUTE_ACTIVE: meeting.get_active(),
        ATTRIBUTE_SOON: meeting.get_soon()
    } for meeting in _meetings]})


# Helper function. Also used for sample data.
def read_meetings_from_data(file_data: dict) -> list[Meeting]:
    return [
        Meeting.from_file(entry_data)
        for entry_data in
        file_data[MEETINGS_FILE_KEY]
    ]


if __name__ == '__main__':
    from doctest import testmod
    testmod()
