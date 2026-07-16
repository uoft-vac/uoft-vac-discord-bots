'''Frodo Meet - Helper
'''
from discord import Message, User
from discord.ext.commands import Bot

from common.util import (
    get_users_from_ping,
    dm_user,
    sub_ids_with_names,
)

from meeting import Meeting


def get_meetings_to_discord(
    meetings: list[Meeting],
    ids_to_names: dict[str: str],
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
            full = 'full' in filters,
            ids_to_names = ids_to_names
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


def parse_participants(message: Message) -> list[str]:
    '''
    Return a list of all pings in a message, omitting all other non-ping parts.
    '''
    return (
        [f'<@&{role.id}>' for role in message.role_mentions] +
        [f'<@{user.id}>' for user in message.mentions]
    )


async def dm_meeting(bot: Bot, meeting: Meeting, message: str, ids_to_names: dict[str: str]) -> list[User]:
    '''
    DM all relevant participants a given message.
    Return a list of users who were failed to DM, if any.

    Note: the given message is IN ADDITION to the greeting on the first line;
    the greeting is sent automatically in this function.
    '''
    failed_users: list[User] = []

    for ping in meeting.get_dm():
        users: list[User] = await get_users_from_ping(bot, ping)

        for user in users:
            if await dm_user(user, (
                f'Hey, {sub_ids_with_names(f'<@{user.id}>', ids_to_names)}! 👋\n'
                f'{message}'
            )) == -1:
                failed_users.append(user)
    
    return failed_users


def build_failed_dm_err(failed_users: list[User], ids_to_names: dict[str: str]) -> str:
    return (
        f'The following user(s) could not be DMed to be notified 🧐: '
        f'{sub_ids_with_names(
            ', '.join([f'**<@{user.id}>**' for user in failed_users]),
            ids_to_names
        )}'
    ) if failed_users else None


if __name__ == '__main__':
    from doctest import testmod
    testmod()
