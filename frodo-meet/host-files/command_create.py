'''Frodo Meet - Create Meeting Command
'''
from discord import Interaction
from discord.ui import Modal, TextInput

from common.common_bot_helper import get_response, ConfirmationViewDefault, NULL_SELECT_VALUE

from frodo_meet_helper import add_meeting, is_title_taken, parse_participants
from frodo_meet_discord_views import RecurrenceSelectView
from frodo_meet_data import save_meetings

from meeting import Meeting
from meeting_time import MeetingTime


async def create_meeting(
    interaction: Interaction,
    meetings: list[Meeting],
    ids_to_names: dict[str: str]
) -> None:
    print('Create meeting command start.')

    print('Sending initial modal.')
    await interaction.response.send_modal(CreateInputModal(
        meetings,
        ids_to_names
    ))


# INITIAL MODAL

class CreateInputModal(Modal, title = 'Create Meeting'):
    _meetings: list[Meeting]
    _ids_to_names: dict[str: str]

    # STEP 1: Get title, time, and description.
    _title_input = TextInput(label = 'Title')
    _time_input = TextInput(label = 'Time')
    _description_input = TextInput(label = 'Description', required = False)

    def __init__(self, meetings: list[Meeting], ids_to_names: dict[str: str]) -> None:
        print('In initial modal, awaiting inputs…')
        super().__init__()
        self._meetings = meetings
        self._ids_to_names = ids_to_names

    async def on_submit(self, interaction: Interaction) -> None:
        print('Got initial inputs.')

        meetings = self._meetings
        title = self._title_input.value

        # If title is taken, send error message and terminate.
        taken_err = is_title_taken(meetings, title)
        if taken_err:
            await interaction.response.send_message(taken_err)
            print('Title taken error, terminating.')
            return

        # If time input was invalid, send error message and terminate.
        time = MeetingTime.from_input(self._time_input.value)
        if isinstance(time, str):
            await interaction.response.send_message(time)
            print('Time error, terminating.')
            return
        
        # STEP 2: Get participants.
        print('Awaiting participants input…')
        await interaction.response.send_message(
            'Enter **pings** for all participants you want to add for this meeting, separated by spaces. (roles or users)\n'
            'E.g. @Lead @Frodo Meet\n'
            'Or type any non-ping message to skip.'
        )
        participants_message = await get_response(interaction)
        print('Got participants.')
        participants = parse_participants(participants_message)

        # Initialise meeting object.
        new_meeting = Meeting(
            self._title_input.value,
            time,
            self._description_input.value,
            participants,
        )

        # STEP 3: Get recurrence, if any.
        print('Sending recurrence select view.')
        await interaction.followup.send(
            content = (
                'Would you like to make this a recurring meeting?\n'
                'For a one-time meeting, select *Normal (one-time)*.'
            ),
            view = RecurrenceSelectView(
                on_select = on_recurrence_select,
                meetings = self._meetings,
                ids_to_names = self._ids_to_names,
                new_meeting = new_meeting
            )
        )


# RECURRENCE SELECT

async def on_recurrence_select(
    interaction: Interaction,
    recurrence: str,
    meetings: list[Meeting],
    ids_to_names: dict[str: str],
    new_meeting: Meeting,
    **_
) -> None:
    print('In on recurrence select.')

    # If a recurrence was selected, set it.
    if recurrence != NULL_SELECT_VALUE:
        new_meeting.set_recurrence(recurrence)

    # STEP 4: Confirmation.
    print('Sending confirmation view.')
    await interaction.response.edit_message(
        content = (
            'New meeting:\n'
            f'{new_meeting.to_discord(full = True, ids_to_names = ids_to_names,)}\n\n'
            'Would you like to create this meeting?'
        ),
        view = ConfirmationViewDefault(
            on_confirm = on_confirm,
            on_cancel = on_cancel,
            meetings = meetings,
            ids_to_names = ids_to_names,
            new_meeting = new_meeting
        )
    )


# CONFIRMATION

async def on_confirm(
    interaction: Interaction,
    meetings: list[Meeting],
    new_meeting: Meeting,
    **_
) -> None:
    print('In on confirm, adding meeting.')

    add_meeting(meetings, new_meeting)
    save_meetings()
    print('Meeting added, data saved.')

    await interaction.message.edit(
        content = f'{new_meeting.get_title(True)} has been created! ✨',
        view = None
    )

    print('Create meeting command end, confirmed.')

async def on_cancel(
    interaction: Interaction,
    new_meeting: Meeting,
    **_
) -> None:
    print('In on cancel.')

    await interaction.message.edit(
        content = f'{new_meeting.get_title(True)} has been discarded! 🗑️',
        view = None
    )

    print('Create meeting command end, cancelled.')
