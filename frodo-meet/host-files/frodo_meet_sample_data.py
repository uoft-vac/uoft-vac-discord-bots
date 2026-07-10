'''Frodo Meet - Sample Data
'''
from common.common_bot_helper import read_json_file

from frodo_meet_data import read_meetings_from_data

from meeting_time import MeetingTime


SAMPLE_MEETINGS_DATA = read_json_file('frodo-meet/meetings_data_sample.json')

SAMPLE_MEETINGS = read_meetings_from_data(SAMPLE_MEETINGS_DATA)

EPOCH = MeetingTime(0)

SAMPLE_IDS_TO_NAMES = {
    '12345': 'Execs',
    '67890': 'Sunny'
}
