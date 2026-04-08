'''Add Command Input Modal
Author: Sunny Lin
Editors: 
Last modified: Apr 7, 26

Input modal for the add command.
'''
from discord import ui, Interaction, ButtonStyle

from common_bot_helper import RESPONSE_TIMEOUT, parse_input

from frodo_meet_commands import add
from frodo_meet_data import write_meetings, DATA_FILE_PATH

from meeting import Meeting
from meeting_time import MeetingTime

LIST_INPUT_BREAKPOINT = ' '


class AddInputModal(ui.Modal, title='Add Meeting'):
    _meetings: list[Meeting]

    _title_input = ui.TextInput(label='Title')
    _time_input = ui.TextInput(label='Time')
    _description_input = ui.TextInput(label='Description', required=False)
    _participants_input = ui.TextInput(label='Participants', required=False)
    _labels_input = ui.TextInput(label='Labels', required=False)

    def __init__(self, meetings: list[Meeting]) -> None:
        super().__init__()
        self._meetings = meetings

    async def on_submit(self, interaction: Interaction):
        # If time input was invalid, print the error message.
        time = MeetingTime.from_input(self._time_input.value)
        if type(time) == str:
            await interaction.response.send_message(time)
            return

        new_meeting = Meeting(
            self._title_input.value,
            time,
            description = self._description_input.value,
            participants = parse_input(self._participants_input.value, LIST_INPUT_BREAKPOINT),
            labels = parse_input(self._labels_input.value, LIST_INPUT_BREAKPOINT),
        )

        await interaction.response.send_message(
            f'New meeting:\n{new_meeting.to_discord(full=True)}\n\nWould you like to save this meeting?',
            view=ConfirmView(self._meetings, new_meeting)
        )


class ConfirmView(ui.View):
    _meetings: list[Meeting]
    _new_meeting: Meeting

    def __init__(self, meetings: list[Meeting], new_meeting: Meeting) -> None:
        super().__init__(timeout=RESPONSE_TIMEOUT)
        self._meetings = meetings
        self._new_meeting = new_meeting

    @ui.button(label="Yes", style=ButtonStyle.green)
    async def confirm(self, interaction: Interaction, _: ui.Button):
        meetings, new_meeting = self._meetings, self._new_meeting

        add(meetings, new_meeting)
        write_meetings(DATA_FILE_PATH, meetings)

        await interaction.response.edit_message(
            content=f'**{new_meeting.get_title()}** has been saved!',
            view=None
        )

    @ui.button(label="No", style=ButtonStyle.red)
    async def cancel(self, interaction: Interaction, _: ui.Button):
        await interaction.response.edit_message(
            content=f'**{self._new_meeting.get_title()}** was discarded.',
            view=None
        )
