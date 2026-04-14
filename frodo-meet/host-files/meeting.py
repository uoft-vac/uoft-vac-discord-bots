'''Meeting class
Author: Sunny Lin
Editors: 
Last modified: Apr 6, 26
'''
from __future__ import annotations

from re import sub

from meeting_time import MeetingTime

SOON_LABEL = 'soon' # Happening in less than <NOTICE_TIME> seconds.
CANCELED_LABEL = 'canceled' # Will not notify.
# Recurring labels: will be cloned the same time next occurrence upon beginning.
YEARLY_LABEL = 'yearly'
WEEKLY_LABEL = 'weekly'
DAILY_LABEL = 'daily'
PAUSED_LABEL = 'paused' # All subsequent meetings will not notify (for recurring meetings).

NON_BEGIN_LABELS = (CANCELED_LABEL, PAUSED_LABEL)
NON_NOTIFY_LABELS = (SOON_LABEL,) + NON_BEGIN_LABELS
RECURRING_LABELS = { # Map recurring labels to corresponding number of seconds to increment the clone.
    YEARLY_LABEL: (365 * 24 * 60 * 60, 'next year'),
    WEEKLY_LABEL: (7 * 24 * 60 * 60, 'next week'),
    DAILY_LABEL: (24 * 60 * 60, 'tomorrow')
}


class Meeting:
    '''
    Contains all attributes of a meeting.

    Default init: args
    '''
    _title: str
    _time: MeetingTime
    _description: str
    _participants: list[str]
    _labels: list[str]

    def __init__(self,
        title: str,
        time: MeetingTime,
        description: str = '',
        participants: list[str] = [],
        labels: list[str] = [],
    ) -> None:
        self._title = title
        self._time = time
        self._description = description
        self._participants = participants
        self._labels = labels
    

    # INITS

    @classmethod
    def from_file(cls, entry_data: dict) -> Meeting:
        return cls(
            entry_data['title'],
            MeetingTime(entry_data['time']),
            entry_data['description'],
            entry_data['participants'],
            entry_data['labels'],
        )
    
    @classmethod
    def clone(cls, original: Meeting, time_inc: int) -> Meeting:
        return cls(
            original.get_title(),
            MeetingTime(original.get_time().get_timestamp() + time_inc),
            original.get_description(),
            original.get_participants(),
            original.get_labels()
        )
    

    # INSTANCE METHODS

    def to_discord(self, ids_to_names: dict[str: str] = None, index: int = None, full: bool = False) -> str:
        '''
        Return a string of the meeting's data to be printed to Discord.

        Sample Usage:

        '''
        time = self.get_time()
        labels = self.get_labels()

        output = '## '

        # If index given, add it.
        if index != None: output += f'{index + 1}. '

        # Add title.
        output += self.get_title()

        # If meeting has any labels, add them in parentheses.
        if labels: output += f' ({', '.join(labels)})'
        
        # Add absolute and relative time on next line.
        output += f'\n{time.to_discord()} ({time.to_discord(True)})'
        
        # If not printing full, return output as it is.
        if not full: return output
        
        # Otherwise, also add description and participants.

        # Add description on next line if there is one.
        description = self.get_description()
        if description: output += f'\n{description}'

        # Add participants on next line.
        participants = self.get_participants()
        if participants:
            output += f'\n__Participants__: {', '.join(participants)}'

            # If not printing to ping, replace all pings with the corresponding role/user's names.
            if ids_to_names != None:
                # print(ids_to_names)
                
                def repl(match): return ids_to_names.get(match.group(1), match.group(0))
                output = sub(r'<@&?(\d+)>', repl, output)
        
        else: output += f'\n__No participants__ 🧐'
        
        return output
    

    def to_display(self, index: int, args: tuple[str]) -> bool:
        ''''
        Given the meeting's index and args,
        returns if the meeting should be displayed.
        Specs are consistent with the show command's docstring.

        Used by show command.

        Sample Usage:
        >>> from sample_data import SAMPLE_MEETINGS

        >>> meeting = SAMPLE_MEETINGS[1]

        >>> meeting.to_display(0, ('all', 'weekly', '-1'))
        False

        >>> meeting.to_display(0, ('-all', '-weekly', '1'))
        True

        >>> meeting.to_display(0, ('-all', 'weekly', '-paused', '2'))
        True

        >>> meeting.to_display(0, ('all', '-paused', '2'))
        False

        >>> meeting.to_display(0, ('all', 'soon', '2'))
        True

        >>> meeting.to_display(0, ('-all', 'soon', '2'))
        False

        >>> meeting.to_display(0, ('soon', '2'))
        False
        '''
        # Refer to normal arguments (nonnegative arguments) as +arguments.

        index_inc = index + 1

        # If index is a -argument, do not display.
        if f'-{index_inc}' in args: return False
        
        # If index is a +argument, display.
        if f'{index_inc}' in args: return True
        
        labels = self.get_labels()
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
    

    def has_labels(self, *labels: str) -> list[str]:
        return list(
            set(self.get_labels()) &
            set(labels)
        )
    

    def is_soon(self, now: MeetingTime, notify_time_secs: int) -> bool:
        return self.get_time().is_within_timeframe(now, notify_time_secs)
    

    def is_past(self, now: MeetingTime) -> bool:
        return self.get_time().is_within_timeframe(now, 0)
    

    # OPERATIONS

    def __lt__(self, other: Meeting) -> bool:
        return \
            self.get_time().get_timestamp() < \
            other.get_time().get_timestamp()
    

    # GETTERS
    def get_title(self, bold: bool = False) -> str: return f'**{self._title}**' if bold else self._title
    def get_time(self) -> MeetingTime: return self._time
    def get_description(self) -> str: return self._description
    def get_participants(self) -> list[str]: return self._participants
    def get_labels(self) -> list[str]: return self._labels

    # SETTERS
    def set_title(self, title: str) -> None: self._title = title
    def set_time(self, time: MeetingTime) -> None: self._time = time
    def set_description(self, description: str) -> None: self._description = description
    def set_participants(self, participants: list[str]) -> None: self._participants = participants
    def set_labels(self, labels: list[str]) -> None: self._labels = labels

    def add_label(self, label: str) -> bool:
        if self.has_labels(label): return False

        self.get_labels().append(label)
        return True


if __name__ == '__main__':
    from doctest import testmod
    testmod()
