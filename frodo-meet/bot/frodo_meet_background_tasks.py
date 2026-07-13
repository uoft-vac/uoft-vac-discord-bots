'''Frodo Meet - Background Tasks
'''
from frodo_meet_helper import add_meeting

from meeting import Meeting, RECURRENCE_MAPPING, RECURRENCE_INC, RECURRENCE_MESSAGE
from meeting_time import MeetingTime


def notify_meetings(meetings: list[Meeting], now: MeetingTime, notice_time_secs: int) -> str:
    '''
    Check if any active meetings not marked as 'soon' is within the notice time.
    Return a string of notify messages for all meetings that this applies to,
    and mark these meetings as 'soon' if they haven't been already.
    Return None if there are no meetings to notify.

    Preconditions:
    - meetings are sorted by time.
    '''
    output_list = []

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

        # Otherwise, add it to the output.

        # If it's the first meeting to notify, record it in case it's the only one.
        if not output_list: first_meeting = curr_meeting

        # Add meeting to notify.
        output_list.append(curr_meeting.to_discord(index = meetings_i, full = True))

        # Mark meeting as soon.
        curr_meeting.set_soon(True)
    
    num_outputs = len(output_list)

    # If there are meetings to notify, return output.
    if num_outputs > 1: return f'The following meetings will begin soon!\n{'\n'.join(output_list)}'
    if num_outputs == 1: return f'{first_meeting.get_title(True)} will begin soon!\n{output_list[0]}'
    
    # Otherwise, there are no meetings to notify, so don't print anything.
    return None


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


if __name__ == '__main__':
    from doctest import testmod
    testmod()
