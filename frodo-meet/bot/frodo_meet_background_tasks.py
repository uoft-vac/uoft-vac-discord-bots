'''Frodo Meet - Background Tasks
'''
from discord import User
from discord.ext.commands import Bot

from common.util import (
    get_users_from_ping,
    sub_ids_with_names,
    dm_user,
)

from frodo_meet_helper import add_meeting
from meeting import Meeting, RECURRENCE_MAPPING, RECURRENCE_INC, RECURRENCE_MESSAGE
from meeting_time import MeetingTime


def notify_meetings(meetings: list[Meeting], now: MeetingTime, notice_time_secs: int) -> tuple[str, dict[str, list[Meeting]]]:
    '''
    Check if any active meetings not marked as 'soon' is within the notice time.
    Return a string of notify messages for all meetings that this applies to,
    and mark these meetings as 'soon' if they haven't been already.
    Return None if there are no meetings to notify.

    Preconditions:
    - meetings are sorted by time.
    '''
    output_list = []
    to_dm: dict[str, list[Meeting]] = {}

    # Check all meetings.
    for meetings_i in range(len(meetings)):
        curr_meeting = meetings[meetings_i]

        # If meeting is not within the notice time,
        # no subsequent meetings can be since they are sorted, so stop checking.
        if not curr_meeting.is_soon(now, notice_time_secs): break

        # If meeting has been notified or is inactive, skip.
        if curr_meeting.get_soon() or not curr_meeting.get_active():
            # Mark meeting as soon.
            curr_meeting.set_soon(True)
            continue

        # Otherwise, notify it.

        # Add meeting to notify.
        output_list.append(curr_meeting.to_discord(index = meetings_i, full = True))

        # Record pings by dms.
        for participant_dm in curr_meeting.get_dm():
            to_dm.setdefault(participant_dm, []).append(curr_meeting)

        # Mark meeting as soon.
        curr_meeting.set_soon(True)

    # Return output and pings to dm if there are any, else None.
    return (
        f'The following meeting(s) will begin soon:\n{'\n'.join(output_list)}'
        if output_list else None,
        to_dm if to_dm else None
    )


def begin_meetings(meetings: list[Meeting], now: MeetingTime) -> str:
    '''
    Return a string of begin messages for all active meetings that have begun.
    For such meetings, remove regular meetings for the meetings list, and
    clone recurring meetings with the appropriate time increment.
    '''
    output = ''

    # Check meetings until they're not past.
    while meetings and meetings[0].is_past(now):

        # Pop the current meeting from the meetings list.
        curr_meeting = meetings.pop(0)

        # If meeting is recurring, clone it with the appropriate time increment.
        recurrence = curr_meeting.get_recurrence()
        if recurrence:
            recurrence_inc = RECURRENCE_MAPPING[recurrence]

            clone = Meeting.clone(curr_meeting, recurrence_inc[RECURRENCE_INC])
            add_meeting(meetings, clone)

            recurring_output = f' and was cloned same time {recurrence_inc[RECURRENCE_MESSAGE]}'
        
        else: recurring_output = ''
        
        # If meeting is active, add it to begin.
        if curr_meeting.get_active():
            output += f'{curr_meeting.get_title(True)} has started{recurring_output}! Happy meeting! 🎈\n'
    
    return output if output else None


async def dm_notifications(
    bot: Bot,
    to_dm: dict[str, list[Meeting]],
    ids_to_names: dict[str: str]
) -> None:
    '''
    Send notifications in DMs for all given pings.
    If ping is a role, send notifications for all members of that role.
    Return a string saying which users were failed to DM, if any.
    '''
    for ping, meetings in to_dm.items():

        # Get users from ping.
        users: list[User] = get_users_from_ping(bot, ping)

        # Construct message.
        message = (
            f'Hey, {sub_ids_with_names(f'<@{user.id}>', ids_to_names)}!\n'
            'Here\'s a reminder that the following meeting(s) will begin soon:\n'
            f'{'\n'.join([
                meeting.to_discord(full = True, ids_to_names = ids_to_names)
                for meeting in meetings
            ])}'
        )

        failed_users: list[User] = []

        # DM all users.
        # If failed to DM, add them to print in the notify channel.
        for user in users:
            if await dm_user(user, message) == -1:
                print(f'Failed to DM {sub_ids_with_names(f'<@{user.id}>')}.')
                failed_users.append(user)
        
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
