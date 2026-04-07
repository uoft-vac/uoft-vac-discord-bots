'''Frodo Meet Commands
Author: Sunny Lin
Editors: 
Last modified: Jul 9, 25

Contains functions to execute tasks and compute outputs for bot commands.
'''
from datetime import datetime, timezone

import frodo_meet_helper
from meeting import Meeting

# Get the parent repo.
from sys import path as sys_path
from os import path as os_path

repo = os_path.abspath(os_path.join(__file__, *('..',) * 3))
sys_path.append(repo)


# CONSTANTS:

LABELS = ( # Constants for all labels; just rename these to change them.
    'soon', # Happening in less than <NOTICE_TIME> seconds.
    'canceled', # Will not notify.
    'weekly', # Will be cloned same time next week upon beginning.
    'paused', # All subsequent meetings will not notify (for weekly meetings).
)

NOTICE_TIME = 5 * 60 # Notify meetings that will begin in less than this value of seconds.


# BOT FUNCTIONS:

def show(args: tuple[str], meetings: list[Meeting], now: float) -> str:
    '''Display the list of meeting plans in order.
    Along with displaying times, also include how much time the meeting is from now.

    By default, display the title, labels, & time of all active meeting plans.

    Arguments can be passed for more options:
    - full: also display description and participants.
    - all: display all meetings on record.
    - <label>: only display meeting plans of that label (multiple allowed).
    - <index>: only display meeting plans of that index (mutliple allowed).
    - -<all/label/index>: do not display meeting plans relevant to -arguments.

    Priority: index > label > all
    If an entry has an argument label and another -argument label, it will still be displayed.

    Preconditions:
    - There cannot be a + and - argument with the same label/index.

    Sample Usage:
    >>> meetings = frodo_meet_helper.get_meetings(frodo_meet_helper.SAMPLE_ENTRIES_DATA)
    >>> sample_now = datetime(2025, 6, 7, 17, 55, tzinfo=timezone.utc).timestamp()

    >>> show((), meetings, sample_now)
    '# 1. General Meeting 1 (soon)\\n2025-06-07 18:00 (0:05 left)\\n\\n# 3. Webmasters - Website\\n2025-06-17 20:00 (10 days, 2:05 left)'

    >>> show(('full',), meetings, sample_now)
    "# 1. General Meeting 1 (soon)\\n2025-06-07 18:00 (0:05 left)\\nOur first exec meeting of the year! Get to know each other and a run down on club operations.\\n**Participants:** <r>11111\\n\\n# 3. Webmasters - Website\\n2025-06-17 20:00 (10 days, 2:05 left)\\nGo over how we should begin coding the club's website.\\n**Participants:** <u>33333, <u>44444"

    >>> show(('all',), meetings, sample_now)
    '# 1. General Meeting 1 (soon)\\n2025-06-07 18:00 (0:05 left)\\n\\n# 2. Weekly Event Recap (weekly, paused)\\n2025-06-13 18:00 (6 days, 0:05 left)\\n\\n# 3. Webmasters - Website\\n2025-06-17 20:00 (10 days, 2:05 left)\\n\\n# 4. Tea Club Collab Meeting (canceled)\\n2025-09-11 16:00 (95 days, 22:05 left)'

    >>> show(('-all',), meetings, sample_now)
    ''

    >>> show(('-all', 'paused', 'canceled'), meetings, sample_now)
    '# 2. Weekly Event Recap (weekly, paused)\\n2025-06-13 18:00 (6 days, 0:05 left)\\n\\n# 4. Tea Club Collab Meeting (canceled)\\n2025-09-11 16:00 (95 days, 22:05 left)'

    >>> show(('-all', '3'), meetings, sample_now)
    '# 3. Webmasters - Website\\n2025-06-17 20:00 (10 days, 2:05 left)'
    '''
    # Turn all args lowercase.
    args = tuple(arg.lower() for arg in args)

    output = ''

    for meetings_i in range(len(meetings)):
        curr_meeting = meetings[meetings_i]
        meeting_labels = curr_meeting.get_labels()

        # If the current entry is not to be displayed, skip.
        if not frodo_meet_helper.to_display(args, meeting_labels, meetings_i + 1): continue

        meeting_time = datetime.fromtimestamp(curr_meeting.get_time(), tz=timezone.utc)

        # Add index and title.
        curr_output = f'# {meetings_i + 1}. {curr_meeting.get_title()}'

        # If meeting has any labels, add them in parentheses.
        if meeting_labels: curr_output += f' ({', '.join(meeting_labels)})'
        
        # Add time and time difference on next line.
        curr_output += f'\n{str(meeting_time)[:-9]} ({ \
            str(meeting_time - datetime.fromtimestamp(now, tz=timezone.utc))[:-3] \
        } left)'
        
        # If "full" is an argument, add description and unformatted participants on separate lines.
        if 'full' in args: curr_output += \
            f'\n{curr_meeting.get_description() \
            }\n**Participants:** {', '.join(curr_meeting.get_participants())}'
        
        # Add current output to overall output.
        output += f'{curr_output}\n\n'
    
    # Return output, omitting last two newlines.
    return output[:-2]


def add(args: tuple[str], meetings: list[Meeting]) -> str:
    '''
    '''


def cancel(args: tuple[str], meetings: list[Meeting]) -> str:
    '''
    '''


def edit(args: tuple[str], meetings: list[Meeting]) -> str:
    '''
    '''


if __name__ == '__main__':
    from doctest import testmod
    testmod()
