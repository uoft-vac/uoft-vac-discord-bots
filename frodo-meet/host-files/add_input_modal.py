'''Add Command Input Modal
Author: Sunny Lin
Editors: 
Last modified: Apr 7, 26

Input modal for the add command.
'''
from discord import ui, Interaction, ButtonStyle

from common_bot_helper import RESPONSE_TIMEOUT, await_message_default

from frodo_meet_commands import add_meeting
from frodo_meet_data import write_meetings, DATA_FILE_PATH

from meeting import Meeting
from meeting_time import MeetingTime

LIST_INPUT_BREAKPOINT = ' '


class AddInputModal(ui.Modal, title='Add Meeting'):
    _meetings: list[Meeting]
    _ids_to_names: dict[str: str]

    _title_input = ui.TextInput(label='Title')
    _time_input = ui.TextInput(label='Time')
    _description_input = ui.TextInput(label='Description', required=False)

    def __init__(self, meetings: list[Meeting], ids_to_names: dict[str: str]) -> None:
        super().__init__()
        self._meetings = meetings
        self._ids_to_names = ids_to_names

    async def on_submit(self, interaction: Interaction):

        # If time input was invalid, print the error message.
        time = MeetingTime.from_input(self._time_input.value)
        if isinstance(time, str):
            await interaction.response.send_message(time)
            return
        
        # Get participants from next message.
        await interaction.response.send_message(
            'Enter **pings** for all participants you want to add for this meeting, separated by spaces. (roles or users)\n'
            'E.g. @Lead @Frodo Meet\n'
            'Or type any non-ping message to skip.'
        )

        try:
            participants_message = await await_message_default(interaction, RESPONSE_TIMEOUT)
        except TimeoutError:
            await interaction.followup.send('Response timeout. ⚠️')
            return
        
        participants = (
            [f"<@&{role.id}>" for role in participants_message.role_mentions] +
            [f"<@{user.id}>" for user in participants_message.mentions]
        )

        # Create meeting object.
        new_meeting = Meeting(
            self._title_input.value,
            time,
            self._description_input.value,
            participants,
        )

        # Await confirmation.
        await interaction.followup.send(
            'New meeting:\n'
            f'{new_meeting.to_discord(self._ids_to_names, full=True)}\n\n'
            'Would you like to create this meeting?',
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

        add_meeting(meetings, new_meeting)
        write_meetings(DATA_FILE_PATH, meetings)

        await interaction.response.edit_message(
            content=f'{new_meeting.get_title(True)} has been created! ✨',
            view=None
        )

    @ui.button(label="No", style=ButtonStyle.red)
    async def cancel(self, interaction: Interaction, _: ui.Button):
        await interaction.response.edit_message(
            content=f'{self._new_meeting.get_title(True)} has been discarded. 🗑️',
            view=None
        )
