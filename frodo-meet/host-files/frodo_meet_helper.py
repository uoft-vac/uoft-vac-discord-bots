'''Frodo Meet Helper
Author: Sunny Lin
Editors:
Last modified: Apr 6, 26

Helper functions for frodo_meet_commands.py.
'''
import common_bot_helper
from meeting import Meeting


# CONSTANTS

# Read data from meeting_entries_sample.json; use this in doctests.
SAMPLE_ENTRIES_DATA = common_bot_helper.read_json_file('frodo-meet/meeting_entries_sample.json')


# HELPER FUNCTIONS:

def get_meetings(file_data: dict) -> list[Meeting]:
    '''
    Given the data from a json file,
    construct and return a list of Meeting objects.

    Sample Usage:
    >>> meetings = get_meetings(SAMPLE_ENTRIES_DATA)
    >>> meeting1 = meetings[0]

    >>> meeting1.get_title()
    'General Meeting 1'

    >>> meeting1.get_time()
    1749319200.0

    >>> meeting1.get_description()
    'Our first exec meeting of the year! Get to know each other and a run down on club operations.'

    >>> meeting1.get_participants()
    ['<r>11111']

    >>> meeting1.get_labels()
    ['soon']

    >>> meeting2 = result[1]

    >>> meeting2.get_title()
    'Weekly Event Recap'

    >>> meeting2.get_time()
    1749837600.0

    >>> meeting2.get_description()
    "Go over today's event. How did it go, anything nice, any improvements for the future, etc."

    >>> meeting2.get_participants()
    ['<r>22222']

    >>> meeting2.get_labels()
    ['weekly', 'paused']
    '''
    return [Meeting.from_file(entry_data) for entry_data in file_data['meetings']]


def to_display(args: tuple[str], labels: list[str], index: int) -> bool:
    ''''
    Returns if a meeting should be displayed according to the arguments.
    Specs are consistent with the show command's docstring.
    For show command.

    Sample Usage:
    >>> to_display(('all', 'weekly', '-1'), ['weekly', 'paused'], 0)
    False

    >>> to_display(('-all', '-weekly', '1'), ['weekly', 'paused'], 0)
    True

    >>> to_display(('-all', 'weekly', '-paused', '2'), ['weekly', 'paused'], 0)
    True

    >>> to_display(('all', '-paused', '2'), ['weekly', 'paused'], 0)
    False

    >>> to_display(('all', 'soon', '2'), ['weekly', 'paused'], 0)
    True

    >>> to_display(('-all', 'soon', '2'), ['weekly', 'paused'], 0)
    False

    >>> to_display(('soon', '2'), ['weekly', 'paused'], 0)
    False

    >>> to_display(('soon', '2'), ['weekly'], 0)
    True
    '''
    # Refer to normal arguments (nonnegative arguments) as +arguments.

    # If index is a -argument, do not display.
    if f'-{index}' in args: return False
    
    # If index is a +argument, display.
    if f'{index}' in args: return True
    
    has_nlabel = False

    # Check labels.
    for label in labels:

        # If has a +argument label, display
        if label in args: return True
        
        # If has a -argument label, record it.
        if f'-{label}' in args: has_nlabel = True
    
    # If has no +argument label but has a -argument label, do not display.
    if has_nlabel: return False
    
    # If "all" is an argument, display.
    if 'all' in args: return True
    
    # If "-all" is an argument, do not display.
    if '-all' in args: return False
    
    # Displayed if it is active (has no canceled or paused label).
    return not ('canceled' in labels or 'paused' in labels)


def update_meeting_record(meetings: list[Meeting], file_path: str) -> None:
    '''
    Given a list of Meeting objects,
    write the data to the json file.

    Sample usage inapplicable.
    '''
    common_bot_helper.write_json_file(file_path, {'meetings': [{
        'title': meeting.get_title(),
        'time': meeting.get_time(),
        'description': meeting.get_description(),
        'participants': meeting.get_participants(),
        'labels': meeting.get_labels(),
    } for meeting in meetings]})


if __name__ == '__main__':
    from doctest import testmod
    testmod()
