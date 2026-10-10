'''Frodo Meet - Background Tasks
'''
from discord.ext.commands import Bot

from common.output import dm_users_from_pings

from frodo_meet_helper import (
    add_meeting,
    build_failed_dm_err,
)
from meeting import (Meeting,
    RECURRENCE_MAPPING,
    RECURRENCE_INC,
    RECURRENCE_MESSAGE,
)
from meeting_time import MeetingTime


def notify_meetings_relative(
    meetings: list[Meeting],
    now: MeetingTime,
    notice_time_secs: int,
    target_notify_status: int = 0
) -> tuple[list[tuple[Meeting, int]], dict[str, list[Meeting]]]:
    '''
    Check if any active meetings not marked as 'soon' is within the notice time.
    Return a list of meeting-to_dm pairs for meetings to notify,
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
        if not curr_meeting.is_within_timeframe(now, notice_time_secs): break

        # If meeting has been notified or is inactive, skip.
        if (
            curr_meeting.get_notify() != target_notify_status or
            not curr_meeting.get_active()
        ): continue

        # Otherwise, notify it.

        # Update notify status.
        curr_meeting.inc_notify()

        # Add meeting to notify.
        output_list.append((curr_meeting, meetings_i))

        # Record pings by dms.
        for participant_dm in curr_meeting.get_dm():
            to_dm.setdefault(participant_dm, []).append(curr_meeting)

    # Return output and pings to dm if there are any, else None.
    return (
        output_list if output_list else None,
        to_dm if to_dm else None
    )


def begin_meetings(meetings: list[Meeting], now: MeetingTime) -> list[tuple[Meeting, str]]:
    '''
    Return a list of meeting-begin message pairs for all active meetings that have begun.
    For such meetings, remove regular meetings for the meetings list, and
    clone recurring meetings with the appropriate time increment.

    Preconditions:
     - meetings are sorted by time.
    '''
    output_list = []

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
            output_list.append((Meeting,
                f'{curr_meeting.get_title(True)} has started{recurring_output}! Happy meeting! 🎈'
            ))
    
    return output_list


async def dm_notifications(
    bot: Bot,
    pings_to_names: dict[str: str],
    to_dm: dict[str, list[Meeting]]
) -> str:
    '''
    Send notifications in DMs for all given names.
    If name is a role, send notifications for all members of that role.
    Return a string saying which users were failed to DM, if any.
    '''

    for name, meetings in to_dm.items():
        failed_dm_users = await dm_users_from_pings(bot, [name], pings_to_names, (
            'Here\'s a reminder that the following meeting(s) are upcoming:\n'
            f'{'\n'.join([
                meeting.to_discord(pings_to_names = pings_to_names)
                for meeting in meetings
            ])}'
        ))

        if failed_dm_users: return build_failed_dm_err(failed_dm_users)


if __name__ == '__main__':
    from doctest import testmod
    testmod()
