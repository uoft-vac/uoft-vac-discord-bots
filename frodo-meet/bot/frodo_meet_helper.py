'''Frodo Meet - Helper
'''
from discord import Interaction, Guild, User

from os import getenv

from common.util import (
    get_pings_to_names,
)

from frodo_meet_data import GETENV_EXEC_ROLE_ID
from meeting import Meeting


def get_meetings_to_discord(
    interaction: Interaction,
    meetings: list[Meeting],
    filters: tuple[str]
) -> str:
    '''
    Display the meetings list in order.
    Along with displaying times, also include how much time the meeting is from now.

    By default, display the title, labels, & time of all active meetings.

    Filters can be passed for more options:
    - full: also display description and participants.
    - all: display all meetings.
    - soon, recurring, daily, weekly, yearly, active: display all meetings relevant to these filters (multiple allowed).
    - <index>: display all meetings of that index (multiple allowed).
    - -<filter>: do not display meetings relevant to -filters (multiple allowed).

    Priority: index > intermediate filters > all
    If a meeting is relevant to both a +filter and a -filter of the same priority, it WILL be displayed.
    '''
    # print(meetings)

    if not meetings: return 'There are no meetings. 🧐'

    output = ''
    for meetings_i in range(len(meetings)):
        curr_meeting = meetings[meetings_i]

        # If meeting shouldn't be displayed, skip.
        if not curr_meeting.to_display(meetings_i, filters): continue
        
        # Add meeting to print.
        output += f'{curr_meeting.to_discord(
            index = meetings_i,
            pings_to_names = (
                get_pings_to_names(interaction.guild) if 'full' in filters else None
            )
        )}\n'
    
    return output if output else 'There are no meetings under such filters. 🧐'


def find_meeting(meetings: list[Meeting], target: str) -> Meeting | str:
    '''
    Given a target string, find a meeting in the meetings list.
    Return the meeting object if found, and an error message otherwise.

    A digit target string will be interpreted as an index (1-indexed):
    - Find the meeting at the corresponding 0-indexed index.
    A non-digit target string will be interpreted as a title:
    - Find the first meeting with the same title.
    
    Sample Usage:
    >>> from frodo_meet_sample_data import SAMPLE_MEETINGS

    >>> meeting1 = SAMPLE_MEETINGS[0]
    >>> meeting11 = SAMPLE_MEETINGS[10]

    # Find by index:
    >>> find_meeting(SAMPLE_MEETINGS, '1') == meeting1
    True

    >>> find_meeting(SAMPLE_MEETINGS, ' 11     ') == meeting11
    True

    # Invalid index:
    >>> index_err = build_find_meeting_index_err(len(SAMPLE_MEETINGS))

    >>> find_meeting(SAMPLE_MEETINGS, '0') == index_err
    True

    >>> find_meeting(SAMPLE_MEETINGS, '12') == index_err
    True

    # Find by title:
    >>> find_meeting(SAMPLE_MEETINGS, 'past, has participants') == meeting1
    True

    >>> find_meeting(SAMPLE_MEETINGS, '   no description, no participants  ') == meeting11
    True

    # Invalid title:
    >>> invalid_title = 'past has participants' # Missing a comma.

    >>> find_meeting(SAMPLE_MEETINGS, invalid_title) == \
            build_find_meeting_title_err(invalid_title)
    True
    '''
    # Strip target string.
    target = target.strip()

    # If target is an index:
    if target.isdigit():
        index = int(target) - 1

        if not 0 <= index < len(meetings):
            return build_find_meeting_index_err(len(meetings))
        
        return meetings[index]
    
    # Otherwise, target is a title:
    for meetings_i in range(len(meetings)):
        curr_meeting = meetings[meetings_i]

        if curr_meeting.get_title().strip().lower() == target.strip().lower():
            return curr_meeting
    
    return build_find_meeting_title_err(target)

def build_find_meeting_index_err(num_meetings: int) -> str:
    return f'Given index is invalid; must be **1–{num_meetings}**. 🧐'

def build_find_meeting_title_err(title: str) -> str:
    return f'No meeting has the title **{title}**. 🧐'


def add_meeting(meetings: list[Meeting], new_meeting: Meeting) -> int:
    '''
    Add the new meeting to the meetings list, and sort it.
    Return the new meeting's index in the sorted list.

    Preconditions:
    - Meetings are sorted by time.
    - New meeting's title is not taken.
    '''
    meetings.append(new_meeting)
    meetings.sort()

    return meetings.index(new_meeting)


def remove_meeting(meetings: list[Meeting], target_meeting: Meeting) -> str:
    '''
    Remove a meeting from the meetings list.
    If the meeting is not in the meetings list, return an error message.
    This is possible, for example, if the meeting began while in the process of removing it.
    Otherwise, return None.
    '''
    if not target_meeting in meetings:
        return f'It seems {target_meeting.get_title(True)} does not exist at the time of confirmation. 🧐'
    
    meetings.remove(target_meeting)


def is_title_taken(meetings: list[Meeting], title: str) -> str:
    '''
    If the given title is taken by a meeting, return an error message.
    Otherwise, return None.
    '''
    for meeting in meetings:
        if title == meeting.get_title():
            return f'A meeting already has the title **{title}**. 🧐'


def get_names_to_pings(guild: Guild) -> dict[str: str]:
    '''
    Return a dictionary of display name-ping pairs for
    all roles and users with the exec role in the server.
    Keys will all be lowercase.
    '''
    names_to_pings = {}

    # Roles:
    for role in guild.roles:
        names_to_pings[role.name.lower()] = f'<@&{role.id}>'

    # Users (execs only):
    for member in guild.get_role(int(getenv(GETENV_EXEC_ROLE_ID))).members:
        names_to_pings[member.display_name.lower()] = f'<@{member.id}>'
    
    print(names_to_pings)
    return names_to_pings


def verify_names(names: list[str], names_to_pings: dict[str: str]) -> list[str]:
    '''Return the list of names that only appear as keys in names_to_pings.'''
    return [name for name in names if name in names_to_pings]


def get_ping_str(participants: list[str], names_to_pings:dict[str: str]) -> str:
    '''
    Return a string of all participants as pings, separated by spaces.
    If ping not found, use the unformatted name.
    '''
    return ' '.join([
        names_to_pings.get(name, name) for name in participants
    ])


def build_failed_dm_err(failed_users: list[User]) -> str:
    return (
        f'The following user(s) could not be DMed to be notified 🧐: {' '.join(failed_users)}'
    ) if failed_users else None


if __name__ == '__main__':
    from doctest import testmod
    testmod()
