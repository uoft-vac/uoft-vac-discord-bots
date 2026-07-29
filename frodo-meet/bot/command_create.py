'''Frodo Meet - Create Meeting Command
'''
from discord import Interaction
from discord.ui import Modal, TextInput

from os import getenv

from common.util import (
    get_response,
    parse_input,
    ConfirmationViewDefault,
    get_pings_to_names,
    dm_users_from_pings,
    NULL_SELECT_VALUE,
)

from frodo_meet_helper import (
    add_meeting,
    is_title_taken,
    get_names_to_pings,
    verify_names,
    build_failed_dm_err,
)
from frodo_meet_discord_views import RecurrenceSelectView
from frodo_meet_data import save_meetings, GETENV_NOTIFY_CHANNEL_ID
from meeting import Meeting, PARTICIPANTS_BREAKPOINTS
from meeting_time import MeetingTime


async def create_meeting(
    interaction: Interaction,
    meetings: list[Meeting]
) -> None:
    print('Create meeting command start.')

    print('Sending initial modal.')
    await interaction.response.send_modal(CreateInputModal(meetings))


# INITIAL MODAL

class CreateInputModal(Modal, title = 'Create Meeting'):
    _meetings: list[Meeting]

    # STEP 1: Get title, time, and description.
    _title_input = TextInput(label = 'Title')
    _time_input = TextInput(label = 'Time')

    def __init__(self, meetings: list[Meeting]) -> None:
        print('In initial modal, awaiting inputs…')
        super().__init__()
        self._meetings = meetings

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

        names_to_pings = get_names_to_pings(interaction.guild)
        
        # STEP 2: Get participants.
        print('Awaiting participants input…')
        await interaction.response.send_message(
            'Enter the **display names** for all participants you want to add for this meeting, separated by commas. (roles or users)\n'
            'E.g. Lead, Frodo Meet\n'
            'Or type an arbitary message to skip.'
        )
        participants_input = await get_response(interaction)
        print('Got participants.')
        participants = [names_to_pings[name] for name in verify_names(
            parse_input(participants_input.content, PARTICIPANTS_BREAKPOINTS),
            names_to_pings
        )]

        # STEP 3: Get pings by DM.
        print('Awaiting pings by dm input…')
        await interaction.followup.send(
            'Enter the display names for all participants you want to be **notified by DM**.\n'
            'Or type an arbitrary message to skip.'
        )
        dm_input = await get_response(interaction)
        print('Got pings by dm.')
        dm = [names_to_pings[name] for name in verify_names(
            parse_input(dm_input.content, PARTICIPANTS_BREAKPOINTS),
            names_to_pings
        )]

        # Initialise meeting object.
        new_meeting = Meeting(
            title = self._title_input.value,
            time = time,
            participants = participants,
            dm = dm,
        )

        # STEP 4: Get recurrence, if any.
        print('Sending recurrence select view.')
        await interaction.followup.send(
            content = (
                'Would you like to make this a recurring meeting?\n'
                'For a one-time meeting, select *Normal (one-time)*.'
            ),
            view = RecurrenceSelectView(
                on_select = on_recurrence_select,
                meetings = self._meetings,
                new_meeting = new_meeting
            )
        )


# RECURRENCE SELECT

async def on_recurrence_select(
    interaction: Interaction,
    meetings: list[Meeting],
    new_meeting: Meeting,
    recurrence: str,
    **_
) -> None:
    print('In on recurrence select.')

    # If a recurrence was selected, set it.
    if recurrence != NULL_SELECT_VALUE:
        new_meeting.set_recurrence(recurrence)

    pings_to_names = get_pings_to_names(interaction.guild)

    # STEP 5: Confirmation.
    print('Sending confirmation view.')
    await interaction.response.edit_message(
        content = (
            'New meeting:\n'
            f'{new_meeting.to_discord(pings_to_names = pings_to_names)}\n\n'
            'Would you like to create this meeting?'
        ),
        view = ConfirmationViewDefault(
            on_confirm = on_confirm,
            on_cancel = on_cancel,
            meetings = meetings,
            pings_to_names = pings_to_names,
            new_meeting = new_meeting
        )
    )


# CONFIRMATION

async def on_confirm(
    interaction: Interaction,
    meetings: list[Meeting],
    pings_to_names: dict[str: str],
    new_meeting: Meeting,
    **_
) -> None:
    print('In on confirm, adding meeting.')

    add_meeting(meetings, new_meeting)
    save_meetings()
    print('Meeting added, data saved.')

    output = (
        f'{new_meeting.get_title(True)} has been __created__! ✨\n'
        f'{new_meeting.to_discord(pings_to_names = pings_to_names)}\n\n'
        'See y\'alls then! 👀'
    )

    await interaction.message.edit(content = output, view = None)

    await interaction.client.get_channel(int(getenv(GETENV_NOTIFY_CHANNEL_ID))).send(
        content = f'{output}\n{' '.join(new_meeting.get_participants())}',
        view = None
    )

    failed_dm_users = await dm_users_from_pings(
        bot = interaction.client,
        pings = new_meeting.get_dm(),
        pings_to_names = pings_to_names,
        message = (
            'Letting you know that you\'ve been **added to a new meeting**:\n'
            f'{new_meeting.to_discord(pings_to_names = pings_to_names)}\n\n'
            'See you there! 👀'
        )
    )

    if failed_dm_users: await interaction.followup.send(
        build_failed_dm_err(failed_dm_users)
    )
    print('DMs have been sent.')

    print('Create meeting command end, confirmed.')

async def on_cancel(
    interaction: Interaction,
    new_meeting: Meeting,
    **_
) -> None:
    print('In on cancel.')

    await interaction.message.edit(
        content = f'{new_meeting.get_title(True)} has been __discarded__! 🗑️',
        view = None
    )

    print('Create meeting command end, cancelled.')
