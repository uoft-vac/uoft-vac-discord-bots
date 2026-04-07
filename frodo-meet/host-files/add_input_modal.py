'''Add Command Input Modal
Author: Sunny Lin
Editors: 
Last modified: Apr 7, 26
'''
from discord import ui, Interaction

from frodo_meet_helper import get_show_meeting_output
from common_bot_helper import parse_input

LIST_INPUT_BREAKPOINT = ' '


class AddInputModal(ui.Modal, title='Add Meeting'):
    _title_input = ui.TextInput(label='Title')
    _time_input = ui.TextInput(label='Time')
    _description_input = ui.TextInput(label='Description', required=False)
    _participants_input = ui.TextInput(label='Participants', required=False)
    _labels_input = ui.TextInput(label='Labels', required=False)

    async def on_submit(self, interaction: Interaction):
        title = self._title_input.value
        time = self._time_input.value
        description = self._description_input.value
        participants = parse_input(self._participants_input.value, LIST_INPUT_BREAKPOINT)
        labels = parse_input(self._labels_input.value, LIST_INPUT_BREAKPOINT)

        await interaction.response.send_message(f'{title} {time} {description} {participants} {labels}')
