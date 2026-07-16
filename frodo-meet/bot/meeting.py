'''Frodo Meet - Meeting Class
'''
from __future__ import annotations

from common.util import sub_ids_with_names

from meeting_time import MeetingTime


ATTRIBUTE_TITLE = 'title'
ATTRIBUTE_TIME = 'time'
ATTRIBUTE_DESCRIPTION = 'description'
ATTRIBUTE_PARTICIPANTS = 'participants'
ATTRIBUTE_DM = 'dm'
ATTRIBUTE_RECURRENCE = 'recurrence'
ATTRIBUTE_ACTIVE = 'active'
ATTRIBUTE_SOON = 'soon'
ATTRIBUTE_RECURRING = 'recurring' # Only used by to_display; not an attribute of a Meeting object.

# Recurrence: will be cloned the same time next occurrence upon beginning.
RECURRENCE_DAILY = 'daily'
RECURRENCE_WEEKLY = 'weekly'
RECURRENCE_YEARLY = 'yearly'

RECURRENCE_INC = False
RECURRENCE_MESSAGE = True
RECURRENCE_MAPPING = { # Map recurring labels to corresponding number of seconds to increment the clone.
    RECURRENCE_DAILY: {
        RECURRENCE_INC: 24 * 60 * 60,
        RECURRENCE_MESSAGE: 'tomorrow'
    },
    RECURRENCE_WEEKLY: {
        RECURRENCE_INC: 7 * 24 * 60 * 60,
        RECURRENCE_MESSAGE: 'next week'
    },
    RECURRENCE_YEARLY: {
        RECURRENCE_INC: 365 * 24 * 60 * 60,
        RECURRENCE_MESSAGE: 'next year'
    }
}

NO_PARTICIPANTS_MESSAGE = '\n__No participants__ 🧐'


class Meeting:
    '''
    Contains all attributes of a meeting.

    Default init: args
    '''
    _title: str
    _time: MeetingTime
    _description: str
    _participants: list[str]
    _dm: list[str]
    _recurrence: str
    _active: bool
    _soon: bool

    def __init__(self,
        title: str,
        time: MeetingTime,
        description: str = '',
        participants: list[str] = [],
        dm: list[str] = [],
        recurrence: str = '',
        active: bool = True,
        soon: bool = False
    ) -> None:
        self._title = title
        self._time = time
        self._description = description
        self._participants = participants
        self._dm = dm
        self._recurrence = recurrence
        self._active = active
        self._soon = soon
    

    # INITS

    @classmethod
    def from_file(cls, entry_data: dict) -> Meeting:
        return cls(
            title = entry_data[ATTRIBUTE_TITLE],
            time = MeetingTime(entry_data[ATTRIBUTE_TIME]),
            description = entry_data[ATTRIBUTE_DESCRIPTION],
            participants = entry_data[ATTRIBUTE_PARTICIPANTS],
            dm = entry_data[ATTRIBUTE_DM],
            recurrence = entry_data[ATTRIBUTE_RECURRENCE],
            active = entry_data[ATTRIBUTE_ACTIVE],
            soon = entry_data[ATTRIBUTE_SOON]
        )
    
    @classmethod
    def clone(cls, original: Meeting, time_inc: int) -> Meeting:
        return cls(
            title = original.get_title(),
            time = MeetingTime(original.get_time().get_timestamp() + time_inc),
            description = original.get_description(),
            participants = original.get_participants(),
            dm = original.get_dm(),
            recurrence = original.get_recurrence(),
            active = original.get_active()
            # Set clone's soon to false.
        )
    

    # INSTANCE METHODS

    def to_discord(self, index: int = None, full: bool = False, ids_to_names: dict[str: str] = None) -> str:
        '''
        Return a string of the meeting's data to be sent in Discord.
        
        Sample Usage:
        >>> from frodo_meet_sample_data import SAMPLE_MEETINGS, SAMPLE_IDS_TO_NAMES

        >>> meeting1 = SAMPLE_MEETINGS[0]
        >>> meeting1.to_discord()
        '## past, has participants\\n<t:0:F> (<t:0:R>)'

        # Index:
        >>> '## 1.' in meeting1.to_discord(0)
        True

        # Full adds description and participants.
        >>> result_full = meeting1.to_discord(0, True)
        >>> 'Will begin.' in result_full
        True
        >>> '__Participants__: <@&12345>, <@67890>' in result_full
        True

        # Ids to names replaces pings with names.
        >>> result_ids = meeting1.to_discord(0, True, SAMPLE_IDS_TO_NAMES)
        >>> 'Execs, Sunny' in result_ids
        True
        >>> '<@&12345>' in result_ids or '<@67890>' in result_ids
        False

        # Extra info (all cases):
        >>> '(daily)' in SAMPLE_MEETINGS[1].to_discord()
        True
        >>> '(weekly, inactive)' SAMPLE_MEETINGS[2].to_discord()
        True
        >>> '(soon)' in SAMPLE_MEETINGS[4].to_discord()
        True
        >>> '(yearly, zoon)' in SAMPLE_MEETINGS[5].to_discord()
        True
        >>> '(inactive)' in SAMPLE_MEETINGS[6].to_discord()
        True
        >>> '(inactive, soon)' in SAMPLE_MEETINGS[7].to_discord()
        True
        >>> '(daily, inactive, soon)' in SAMPLE_MEETINGS[8].to_discord()
        True

        # No participants:
        >>> meeting_no_participants = SAMPLE_MEETINGS[10]
        >>> meeting_no_participants.to_discord(full = True) == \
                meeting_no_participants.to_discord(full = True, ids_to_names = SAMPLE_IDS_TO_NAMES) == \
                NO_PARTICIPANTS_MESSAGE
        True
        '''
        time = self.get_time()

        output = '## '

        # If index given, add it.
        if index != None: output += f'{index + 1}. '

        # Add title.
        output += self.get_title()

        # If meeting has any extra info, add them in parentheses.
        # This includes recurrence if it has one, if it's inactive, and if it's soon.
        recurrence = self.get_recurrence()
        extra_info = ', '.join(
            ([recurrence] if recurrence else []) +
            (['inactive'] if not self.get_active() else []) +
            (['soon'] if self.get_soon() else [])
        )
        if extra_info:
            output += f' ({extra_info})'
        
        # Add absolute and relative time on next line.
        output += f'\n{time.to_discord()} ({time.to_discord(True)})'
        
        # If not printing full, return output as it is.
        if not full: return output
        
        # Otherwise, also add description, participants, and pings by dm.

        # Add description on next line, if there is one.
        description = self.get_description()
        if description: output += f'\n{description}'

        # Add participants on next line.
        participants = self.get_participants()
        output += (
            f'\n__Participants__: {', '.join(participants)}'
            if participants
            else NO_PARTICIPANTS_MESSAGE
        )
        
        # Add pings by dm on next line, if there are any.
        dm = self.get_dm()
        if dm: output += f'\n- __Ping by DM__: {', '.join(dm)}'
        
        # If not printing to ping, replace all pings with the corresponding role/user's names.
        # This will run even if no pings were added to the output; in any case, no repercussions.
        if ids_to_names != None:
            # print(ids_to_names)
            output = sub_ids_with_names(output, ids_to_names)
        
        return output

    def to_display(self, index: int, filters: tuple[str]) -> bool:
        ''''
        Given the meeting's index and filters,
        returns if the meeting should be displayed.
        Specs are consistent with the show command's docstring.
        
        Sample Usage:
        >>> from frodo_meet_sample_data import SAMPLE_MEETINGS

        >>> meeting_all_filters = SAMPLE_MEETINGS[5]
        >>> meeting_all_filters.to_display(0, ())
        True
        >>> meeting_all_filters.to_display(0, ('-all',))
        False

        # Intermediate filters have priority over all.
        >>> meeting_all_filters.to_display(0, ('-all', 'recurring'))
        True
        >>> meeting_all_filters.to_display(0, ('-all', 'yearly'))
        True
        >>> meeting_all_filters.to_display(0, ('-all', 'soon'))
        True
        >>> meeting_all_filters.to_display(0, ('all', '-recurring'))
        False
        >>> meeting_all_filters.to_display(0, ('all', '-yearly'))
        False
        >>> meeting_all_filters.to_display(0, ('all', '-soon'))
        False
        >>> meeting_all_filters.to_display(0, ('all', '-active'))
        False

        # Index has priority over intermediate filters and all.
        >>> meeting_all_filters.to_display(0, ('-all', '-recurring', '1'))
        True
        >>> meeting_all_filters.to_display(0, ('all', 'recurring', '-1'))
        False

        # Filters irrelevant to the meeting have no effect.
        >>> meeting_all_filters.to_display(0, ('-all', 'daily'))
        False
        >>> meeting_all_filters.to_display(0, ('-all', '-recurring', '2'))
        False

        # Inactive meetings are not displayed by default.
        >>> meeting_inactive = SAMPLE_MEETINGS[2]
        >>> meeting_inactive.to_display(0, ())
        False
        >>> meeting_inactive.to_display(0, ('all',))
        True
        '''
        # Refer to normal filters (nonnegative filters) as +filters.

        index_inc = index + 1

        # Turn all filters lowercase.
        filters = [filter.lower() for filter in filters]

        # If index is a +filter, display.
        if f'{index_inc}' in filters: return True
        
        # If index is a -filter, don't display.
        if f'-{index_inc}' in filters: return False

        recurrence = self.get_recurrence()

        # If relevant to any intermediate filters, display.
        # Don't check active since it's default.
        if ATTRIBUTE_SOON in filters and self.get_soon() or \
        recurrence and (recurrence in filters or 'recurring' in filters):
            return True

        # Otherwise, if relevant to any -intermediate filters, don't display.
        if f'-{ATTRIBUTE_SOON}' in filters and self.get_soon() or \
        recurrence and (f'-{recurrence}' in filters or '-recurring' in filters) or \
        f'-{ATTRIBUTE_ACTIVE}' in filters and self.get_active():
            return False
        
        # If "all" is an argument, display.
        if 'all' in filters: return True
        
        # If "-all" is an argument, do not display.
        if '-all' in filters: return False
        
        # Displayed if it is active.
        return self.get_active()
    

    def is_soon(self, now: MeetingTime, notify_time_secs: int) -> bool:
        return self.get_time().is_within_timeframe(now, notify_time_secs)
    

    def is_past(self, now: MeetingTime) -> bool:
        return self.get_time().is_within_timeframe(now, 0)
    

    # OPERATIONS

    def __lt__(self, other: Meeting) -> bool:
        return (
            self.get_time().get_timestamp() < 
            other.get_time().get_timestamp()
        )
    

    # GETTERS
    def get_title(self, bold: bool = False) -> str: return f'**{self._title}**' if bold else self._title
    def get_time(self) -> MeetingTime: return self._time
    def get_description(self) -> str: return self._description
    def get_participants(self) -> list[str]: return self._participants
    def get_dm(self) -> list[str]: return self._dm
    def get_recurrence(self) -> str: return self._recurrence
    def get_active(self) -> bool: return self._active
    def get_soon(self) -> bool: return self._soon


    # SETTERS
    def set_title(self, title: str) -> None: self._title = title
    def set_time(self, time: MeetingTime) -> None: self._time = time
    def set_description(self, description: str) -> None: self._description = description
    def set_participants(self, participants: list[str]) -> None: self._participants = participants
    def set_dm(self, dm: list[str]) -> None: self._dm = dm
    def set_recurrence(self, recurrence: str) -> None: self._recurrence = recurrence
    def set_active(self, active: bool = True) -> None: self._active = active
    def set_soon(self, soon: bool = False) -> None: self._soon = soon

    def toggle_active(self) -> bool:
        new_active = not self.get_active()
        self._active = new_active
        return new_active


if __name__ == '__main__':
    from doctest import testmod
    testmod()
