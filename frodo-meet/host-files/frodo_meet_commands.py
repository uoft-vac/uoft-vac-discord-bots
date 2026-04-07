'''Frodo Meet Commands
Author: Sunny Lin
Editors: 
Last modified: Jul 9, 25

Contains functions to execute tasks and compute outputs for bot commands.
'''
import frodo_meet_helper
from meeting import Meeting


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
    '''
    Display the list of meeting plans in order.
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

    >>> show((), meetings, frodo_meet_helper.SAMPLE_NOW)
    '## 1. General Meeting 1 (soon)\\n2025-06-07 18:00 (0:05 left)\\n## 3. Webmasters - Website\\n2025-06-17 20:00 (10 days, 2:05 left)'

    >>> show(('full',), meetings, frodo_meet_helper.SAMPLE_NOW)
    "## 1. General Meeting 1 (soon)\\n2025-06-07 18:00 (0:05 left)\\nOur first exec meeting of the year! Get to know each other and a run down on club operations.\\n**Participants:** <r>11111\\n## 3. Webmasters - Website\\n2025-06-17 20:00 (10 days, 2:05 left)\\nGo over how we should begin coding the club's website.\\n**Participants:** <u>33333, <u>44444"

    >>> show(('all',), meetings, frodo_meet_helper.SAMPLE_NOW)
    '## 1. General Meeting 1 (soon)\\n2025-06-07 18:00 (0:05 left)\\n## 2. Weekly Event Recap (weekly, paused)\\n2025-06-13 18:00 (6 days, 0:05 left)\\n## 3. Webmasters - Website\\n2025-06-17 20:00 (10 days, 2:05 left)\\n## 4. Tea Club Collab Meeting (canceled)\\n2025-09-11 16:00 (95 days, 22:05 left)'

    >>> show(('-all',), meetings, frodo_meet_helper.SAMPLE_NOW)
    ''

    >>> show(('-all', 'paused', 'canceled'), meetings, frodo_meet_helper.SAMPLE_NOW)
    '## 2. Weekly Event Recap (weekly, paused)\\n2025-06-13 18:00 (6 days, 0:05 left)\\n## 4. Tea Club Collab Meeting (canceled)\\n2025-09-11 16:00 (95 days, 22:05 left)'

    >>> show(('-all', '3'), meetings, frodo_meet_helper.SAMPLE_NOW)
    '## 3. Webmasters - Website\\n2025-06-17 20:00 (10 days, 2:05 left)'
    '''
    # print(meetings)

    # Turn all args lowercase.
    args = tuple(arg.lower() for arg in args)

    output = ''
    for meetings_i in range(len(meetings)):
        curr_meeting = meetings[meetings_i]

        # If the current entry is not to be displayed, skip.
        if not frodo_meet_helper.to_display(args, curr_meeting.get_labels(), meetings_i): continue
        
        # Compute and add the output for the meeting.
        output += f'{frodo_meet_helper.get_show_meeting_output(
            curr_meeting,
            meetings_i,
            now,
            'full' in args
        )}\n'
    
    # Return output, omitting the last \n.
    return output[:-1]


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
