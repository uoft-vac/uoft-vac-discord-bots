'''Frodo Meet Data
Author: Sunny Lin
Editors:
Last modified: Apr 6, 26

Functions to fetch from and write to files data.
'''
from common_bot_helper import read_json_file, write_json_file
from meeting import Meeting
from meeting_time import MeetingTime

# Data file path
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE_PATH = BASE_DIR / 'meetings_data.json'

# Sample data
SAMPLE_MEETINGS_DATA = read_json_file('frodo-meet/meetings_data_sample.json')
EPOCH = MeetingTime(0)


def get_meetings(file_data: dict) -> list[Meeting]:
    '''
    Given the data from a json file, construct and return a list of Meeting objects.
    '''
    return [Meeting.from_file(entry_data) for entry_data in file_data['meetings']]

SAMPLE_MEETINGS = get_meetings(SAMPLE_MEETINGS_DATA) # Sample data


def write_meetings(file_path: str, meetings: list[Meeting]) -> None:
    '''
    Given a list of Meeting objects, write the data to the json file.

    Sample usage inapplicable.
    '''
    write_json_file(file_path, {'meetings': [{
        'title': meeting.get_title(),
        'time': meeting.get_time().get_timestamp(),
        'description': meeting.get_description(),
        'participants': meeting.get_participants(),
        'labels': meeting.get_labels(),
    } for meeting in meetings]})


if __name__ == '__main__':
    from doctest import testmod
    testmod()
