'''Frodo Meet Bot Commands
Author: Sunny Lin
Editors: 
Last modified: Apr 8, 26

Functions to execute tasks and compute outputs for bot commands.
'''
from meeting import Meeting, SOON_LABEL, NON_NOTIFY_LABELS
from meeting_time import MeetingTime


# BOT FUNCTIONS

def show(args: tuple[str], meetings: list[Meeting]) -> str:
    '''
    Display the list of meetings in order.
    Along with displaying times, also include how much time the meeting is from now.

    By default, display the title, labels, & time of active meetings.

    Args can be passed for more options:
    - full: also display description and participants.
    - all: display all meetings on record.
    - <label>: only display meetings of that label (multiple allowed).
    - <index>: only display meetings of that index (mutliple allowed).
    - -<all/label/index>: do not display meetings relevant to -args.

    Priority: index > label > all
    If a meeting has an arg label and another -arg label, it will still be displayed.

    Preconditions:
    - There cannot be a + and - arg with the same label/index.

    Sample Usage:
    
    '''
    # print(meetings)

    # Turn all args lowercase.
    args = tuple(arg.lower() for arg in args)

    output = ''
    for meetings_i in range(len(meetings)):
        curr_meeting = meetings[meetings_i]

        # If current entry is not to be displayed, skip.
        if not curr_meeting.to_display(meetings_i, args): continue
        
        # Compute and add the output for the meeting.
        output += f'{curr_meeting.to_discord(meetings_i, 'full' in args)}\n'
    
    # Return output, omitting the last \n.
    return output[:-1]


def add(meetings: list[Meeting], new_meeting: Meeting) -> int:
    '''
    Add the new meeting to the list of meetings, and sort it.
    Return the new meeting's index in the sorted list.

    Sample Usage:
    >>> from copy import deepcopy
    >>> from frodo_meet_data import SAMPLE_MEETINGS

    >>> meetings = deepcopy(SAMPLE_MEETINGS)
    >>> new_meeting = Meeting('New meeting', MeetingTime(15), 'Will be inserted at index 1 (second meeting)', [], [])

    >>> add(meetings, new_meeting)
    1

    >>> meetings[1].get_title()
    'New meeting'
    '''
    meetings.append(new_meeting)
    meetings.sort()

    return meetings.index(new_meeting)


def notify(meetings: list[Meeting], now: MeetingTime, notice_time_secs: int) -> str | None:
    '''
    Check if any meetings without the 'soon' label is within the notice time.
    Return a string of notify messages for all meetings that this applies to,
    and mark these meetings as 'soon' if they haven't been already.
    Return None if there are no meetings to notify.

    Preconditions:
    - meetings are sorted by timestamp.

    Sample Usage:
    >>> from copy import deepcopy
    >>> from frodo_meet_data import SAMPLE_MEETINGS, EPOCH

    >>> meetings = deepcopy(SAMPLE_MEETINGS)

    # Meetings that are notified will be marked as soon.
    >>> m0, m2, m3 = meetings[0], meetings[2], meetings[3]
    >>> m0.has_labels(SOON_LABEL) or m2.has_labels(SOON_LABEL) or m3.has_labels(SOON_LABEL)
    False

    # Notice time = 10: will only notify first meeting.
    >>> notify(meetings, EPOCH, 10)
    '**No labels, soon** will begin soon!\\n## 1. No labels, soon\\n<t:10:F> (<t:10:R>)\\nWill notify and be marked as soon.\\n__Participants__: <@&12345>'
    >>> m0.has_labels(SOON_LABEL)
    True

    # Notice time = 40: will only notify the fourth meeting since
    # the second and third are marked and canceled respectively.
    # First has been marked as soon, so will not notify again.
    >>> notify(meetings, EPOCH, 40)
    '**No description** will begin soon!\\n## 4. No description\\n<t:40:F> (<t:40:R>)\\n__No participants__ 🧐'
    >>> m2.has_labels(SOON_LABEL) and m3.has_labels(SOON_LABEL)
    True

    >>> meetings = deepcopy(SAMPLE_MEETINGS)

    # Notice time = 40: will notify both first and fourth meeting.
    >>> notify(meetings, EPOCH, 40)
    'The following meetings will begin soon!\\n## 1. No labels, soon\\n<t:10:F> (<t:10:R>)\\nWill notify and be marked as soon.\\n__Participants__: <@&12345>\\n## 4. No description\\n<t:40:F> (<t:40:R>)\\n__No participants__ 🧐'
    '''
    output_list = []

    # Check all meetings.
    for meetings_i in range(len(meetings)):
        curr_meeting = meetings[meetings_i]

        # If meeting is not within the notice time,
        # no subsequent meetings can be since they are sorted, so stop checking.
        if not curr_meeting.is_soon(now, notice_time_secs): break

        # If meeting has any non-notify labels, skip.
        if curr_meeting.has_labels(*NON_NOTIFY_LABELS):
            # Mark meeting as soon if applicable.
            curr_meeting.add_label(SOON_LABEL)
            continue

        # Otherwise, add it to the output.

        # If it's the first meeting to notify, record it in case it's the only one.
        if not output_list: first_meeting = curr_meeting

        # Add meeting to notify.
        output_list.append(curr_meeting.to_discord(meetings_i, True, True))

        # Mark meeting as soon.
        curr_meeting.add_label(SOON_LABEL)
    
    num_outputs = len(output_list)

    # If there are meetings to notify, return output.
    if num_outputs > 1: return f'The following meetings will begin soon!\n{'\n'.join(output_list)}'
    if num_outputs == 1: return f'**{first_meeting.get_title()}** will begin soon!\n{output_list[0]}'
    
    # Otherwise, there are no meetings to notify, so don't print anything.
    return None


if __name__ == '__main__':
    from doctest import testmod
    testmod()
