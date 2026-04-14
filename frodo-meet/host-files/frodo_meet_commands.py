'''Frodo Meet Bot Commands
Author: Sunny Lin
Editors: 
Last modified: Apr 8, 26

Functions to execute tasks and compute outputs for bot commands.
'''
from meeting import Meeting, \
    SOON_LABEL, \
    NON_NOTIFY_LABELS, \
    NON_BEGIN_LABELS, \
    RECURRING_LABELS
from meeting_time import MeetingTime


# BOT FUNCTIONS

def show_meetings(args: tuple[str], meetings: list[Meeting], ids_to_names: dict[str: str]) -> str:
    '''
    Display the meetings list in order.
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
    >>> from frodo_meet_data import SAMPLE_MEETINGS, SAMPLE_IDS_TO_NAMES

    >>> show_meetings((), [], {})
    'There are no meetings. 🧐'
    
    >>> show_meetings((), SAMPLE_MEETINGS, SAMPLE_IDS_TO_NAMES)
    '## 1. past\\n<t:0:F> (<t:0:R>)\\n## 2. past, has soon, daily, multiple participants (soon, daily)\\n<t:0:F> (<t:0:R>)\\n## 5. no description\\n<t:20:F> (<t:20:R>)\\n## 6. not soon\\n<t:1000:F> (<t:1000:R>)'

    >>> show_meetings(('full',), SAMPLE_MEETINGS, SAMPLE_IDS_TO_NAMES)
    '## 1. past\\n<t:0:F> (<t:0:R>)\\nnotify: will notify and mark as soon. begin: will begin and be removed\\n__Participants__: Execs\\n## 2. past, has soon, daily, multiple participants (soon, daily)\\n<t:0:F> (<t:0:R>)\\nnotify: will not notify since marked as soon. begin: will begin, be removed, and be cloned tomorrow\\n__Participants__: Execs, Sunny\\n## 5. no description\\n<t:20:F> (<t:20:R>)\\n__No participants__ 🧐\\n## 6. not soon\\n<t:1000:F> (<t:1000:R>)\\nwill not notify or begin\\n__No participants__ 🧐'

    >>> show_meetings(('all',), SAMPLE_MEETINGS, SAMPLE_IDS_TO_NAMES)
    '## 1. past\\n<t:0:F> (<t:0:R>)\\n## 2. past, has soon, daily, multiple participants (soon, daily)\\n<t:0:F> (<t:0:R>)\\n## 3. past, weekly, paused, no participants (weekly, paused)\\n<t:0:F> (<t:0:R>)\\n## 4. soon, canceled (canceled)\\n<t:10:F> (<t:10:R>)\\n## 5. no description\\n<t:20:F> (<t:20:R>)\\n## 6. not soon\\n<t:1000:F> (<t:1000:R>)'
    
    >>> show_meetings(('all', '-soon', '-1'), SAMPLE_MEETINGS, SAMPLE_IDS_TO_NAMES)
    '## 3. past, weekly, paused, no participants (weekly, paused)\\n<t:0:F> (<t:0:R>)\\n## 4. soon, canceled (canceled)\\n<t:10:F> (<t:10:R>)\\n## 5. no description\\n<t:20:F> (<t:20:R>)\\n## 6. not soon\\n<t:1000:F> (<t:1000:R>)'

    >>> show_meetings(('-all',), SAMPLE_MEETINGS, SAMPLE_IDS_TO_NAMES)
    ''

    >>> show_meetings(('-all', 'paused', '4'), SAMPLE_MEETINGS, SAMPLE_IDS_TO_NAMES)
    '## 3. past, weekly, paused, no participants (weekly, paused)\\n<t:0:F> (<t:0:R>)\\n## 4. soon, canceled (canceled)\\n<t:10:F> (<t:10:R>)'
    '''
    # print(meetings)

    if not meetings: return 'There are no meetings. 🧐'

    # Turn all args lowercase.
    args = tuple(arg.lower() for arg in args)

    output = ''
    for meetings_i in range(len(meetings)):
        curr_meeting = meetings[meetings_i]

        # If current entry is not to be displayed, skip.
        if not curr_meeting.to_display(meetings_i, args): continue
        
        # Compute and add the output for the meeting.
        output += f'{curr_meeting.to_discord(ids_to_names, meetings_i, 'full' in args)}\n'
    
    # Return output, omitting the last \n.
    return output[:-1]


def add_meeting(meetings: list[Meeting], new_meeting: Meeting) -> int:
    '''
    Add the new meeting to the meetings list, and sort it.
    Return the new meeting's index in the sorted list.

    Sample Usage:
    >>> from copy import deepcopy
    >>> from frodo_meet_data import SAMPLE_MEETINGS

    >>> meetings = deepcopy(SAMPLE_MEETINGS)

    >>> new_meeting = Meeting('new meeting', MeetingTime(5), 'will be inserted at index 3 (after past meetings)', [], [])

    >>> index = add_meeting(meetings, new_meeting)
    >>> index
    3

    >>> meetings[index].get_title()
    'new meeting'
    '''
    meetings.append(new_meeting)
    meetings.sort()

    return meetings.index(new_meeting)


def notify_meetings(meetings: list[Meeting], now: MeetingTime, notice_time_secs: int) -> str:
    '''
    Check if any active meetings not marked as 'soon' is within the notice time.
    Return a string of notify messages for all meetings that this applies to,
    and mark these meetings as 'soon' if they haven't been already.
    Return None if there are no meetings to notify.

    Preconditions:
    - meetings are sorted by timestamp.

    Sample Usage:
    >>> from copy import deepcopy
    >>> from frodo_meet_data import SAMPLE_MEETINGS, EPOCH

    >>> meetings = deepcopy(SAMPLE_MEETINGS)

    >>> m0, m2, m3 = meetings[0], meetings[2], meetings[3]
    >>> m0.has_labels(SOON_LABEL) or m2.has_labels(SOON_LABEL) or m3.has_labels(SOON_LABEL)
    []

    >>> notify_meetings(meetings, EPOCH, 10)
    '**past** will begin soon!\\n## 1. past\\n<t:0:F> (<t:0:R>)\\nnotify: will notify and mark as soon. begin: will begin and be removed\\n__Participants__: <@&12345>'

    >>> m0.has_labels(SOON_LABEL) and m2.has_labels(SOON_LABEL)
    ['soon']

    >>> notify_meetings(meetings, EPOCH, 20)
    '**no description** will begin soon!\\n## 5. no description\\n<t:20:F> (<t:20:R>)\\n__No participants__ 🧐'

    >>> m3.has_labels(SOON_LABEL)
    ['soon']

    >>> meetings = deepcopy(SAMPLE_MEETINGS)

    >>> notify_meetings(meetings, EPOCH, 20)
    'The following meetings will begin soon!\\n## 1. past\\n<t:0:F> (<t:0:R>)\\nnotify: will notify and mark as soon. begin: will begin and be removed\\n__Participants__: <@&12345>\\n## 5. no description\\n<t:20:F> (<t:20:R>)\\n__No participants__ 🧐'
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
        output_list.append(curr_meeting.to_discord(index=meetings_i, full=True))

        # Mark meeting as soon.
        curr_meeting.add_label(SOON_LABEL)
    
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

    Sample Usage:
    >>> from copy import deepcopy
    >>> from frodo_meet_data import SAMPLE_MEETINGS, EPOCH

    >>> meetings = deepcopy(SAMPLE_MEETINGS)

    >>> begin_meetings(meetings, EPOCH)
    '**past** has started! Happy meeting! 🎈\\n**past, has soon, daily, multiple participants** has started and was cloned same time tomorrow! Happy meeting! 🎈\\n'

    >>> [meeting.get_title() for meeting in meetings]
    ['soon, canceled', 'no description', 'not soon', 'past, has soon, daily, multiple participants', 'past, weekly, paused, no participants']

    >>> meetings[3].get_time().get_timestamp()
    86400.0

    >>> meetings[4].get_time().get_timestamp()
    604800.0

    >>> meetings[3].get_time().get_timestamp() == RECURRING_LABELS['daily'][0]
    True

    >>> meetings[4].get_time().get_timestamp() == RECURRING_LABELS['weekly'][0]
    True
    '''
    output = ''

    # Check meetings until they're not past.
    while meetings and meetings[0].is_past(now):

        # Pop the current meeting from the meetings list.
        curr_meeting = meetings.pop(0)

        # If meeting is recurring, clone it with the appropriate time increment.
        recurring_label = curr_meeting.has_labels(*RECURRING_LABELS.keys())
        if recurring_label:
            recurring_label_result = RECURRING_LABELS[recurring_label[0]]

            clone = Meeting.clone(curr_meeting, recurring_label_result[0])
            add_meeting(meetings, clone)

            recurring_output = f' and was cloned same time {recurring_label_result[1]}'
        
        else: recurring_output = ''
        
        # If meeting is active, add it to begin.
        if not curr_meeting.has_labels(*NON_BEGIN_LABELS):
            output += f'{curr_meeting.get_title(True)} has started{recurring_output}! Happy meeting! 🎈\n'
    
    return output if output else None


if __name__ == '__main__':
    from doctest import testmod
    testmod()
