'''Frodo Meet - Discord Views
'''
from discord import Interaction, SelectOption
from discord.ui import View, Select

from common.common_bot_helper import RESPONSE_TIMEOUT, NULL_SELECT_VALUE, MAX_SELECTS

from frodo_meet_helper import find_meeting

from meeting import Meeting,\
    RECURRENCE_DAILY,\
    RECURRENCE_WEEKLY,\
    RECURRENCE_YEARLY


# MEETING SELECT

class MeetingSelectView(View):
    def __init__(self,
        on_select: callable,
        meetings: list[Meeting],
        timeout: float = RESPONSE_TIMEOUT,
        **data: dict
    ) -> None:
        print('In meeting select view, awaiting target meeting select…')
        super().__init__(timeout = timeout)

        self.add_item(MeetingSelect(
            on_select,
            meetings,
            data
        ))
    
class MeetingSelect(Select):
    _on_select: callable
    _meetings: list[Meeting]
    _data: dict

    def __init__(self,
        on_select: callable,
        meetings: list[Meeting],
        data: dict
    ) -> None:
        self._on_select = on_select
        self._meetings = meetings
        self._data = data

        super().__init__(
            placeholder = 'Select meeting…',
            options = [
                SelectOption(
                    label = f'{meetings_i + 1}. {meeting.get_title()}',
                    value = meeting.get_title()
                    # Does not use index as values since an index can still be valid even if the target meeting no longer exists.
                    # Use titles since they are unique.
                )
                for meetings_i, meeting in enumerate(meetings[:MAX_SELECTS])
            ]
        )

    async def callback(self, interaction: Interaction):
        print('Meeting selected, finding target meeting.')
        meetings = self._meetings

        # Get target meeting.
        target_meeting = find_meeting(meetings, self.values[0])
        if isinstance(target_meeting, str):
            await interaction.followup.send(target_meeting)
            print('Find meeting error, terminating.')
            return

        # Execute followup process.
        print('Got target meeting, executing followup process for meeting select.')
        await self._on_select(
            interaction,
            self._meetings,
            **self._data
        )


# RECURRENCE SELECT

class RecurrenceSelectView(View):
    def __init__(self,
        on_select: callable,
        timeout: float = RESPONSE_TIMEOUT,
        **data: dict
    ) -> None:
        print('In recurrence select view, awaiting recurrence select…')
        super().__init__(timeout = timeout)

        self.add_item(RecurrenceSelect(on_select, data))

class RecurrenceSelect(Select):
    _on_select: callable
    _data: dict

    def __init__(self,
        on_select: callable,
        data: dict
    ) -> None:
        self._on_select = on_select
        self._data = data

        super().__init__(
            placeholder = 'Select recurrence option…',
            options = [
                SelectOption(label = 'Normal (one-time)', value = NULL_SELECT_VALUE),
                SelectOption(label = RECURRENCE_DAILY.capitalize(), value = RECURRENCE_DAILY),
                SelectOption(label = RECURRENCE_WEEKLY.capitalize(), value = RECURRENCE_WEEKLY),
                SelectOption(label = RECURRENCE_YEARLY.capitalize(), value = RECURRENCE_YEARLY),
            ]
        )
    
    async def callback(self, interaction: Interaction) -> None:
        print('Recurrence selected.')
        recurrence = self.values[0]

        # Execute followup process.
        print('Executing followup process for recurrence select.')
        await self._on_select(
            interaction,
            recurrence,
            **self._data
        )
