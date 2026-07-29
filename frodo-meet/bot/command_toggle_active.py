'''Frodo Meet - Toggle Active Command
'''
from discord import Interaction

from os import getenv

from common.util import (
    ConfirmationViewDefault,
    get_pings_to_names,
    dm_users_from_pings,
)

from frodo_meet_helper import (
    get_meetings_to_discord,
    find_meeting,
    build_failed_dm_err,
)
from frodo_meet_data import save_meetings, GETENV_NOTIFY_CHANNEL_ID
from frodo_meet_discord_views import MeetingSelectView
from meeting import Meeting


async def toggle_active(
    interaction: Interaction,
    meetings: list[Meeting],
    target: str
) -> None:
    print('Toggle active command start.')

    if not meetings:
        await interaction.response.send_message('There are no meetings to toggle. 🧐')
        print('No meetings, terminating.')
        return
    
    # If no target arg was given, get meeting select.
    if not target:
        print('No target string, sending meeting select view.')
        await interaction.response.send_message(
            content = (
                f'Enter the title or index of the meeting whose active status you want to toggle:\n'
                f'{get_meetings_to_discord(interaction, meetings, ('all',))}'
            ),
            view = MeetingSelectView(
                on_select = on_meeting_select,
                meetings = meetings,
            )
        )
        return
    
    # Get target meeting.
    print('Have target string, finding target meeting.')
    target_meeting = find_meeting(meetings, target)
    if isinstance(target_meeting, str):
        await interaction.response.send_message(target_meeting)
        print('Find meeting error, terminating.')
        return
    
    # Confirmation.
    print('Got target meeting, sending confirmation view.')

    pings_to_names = get_pings_to_names(interaction.guild)

    await interaction.response.send_message(
        content = build_confirmation_content(
            target_meeting = target_meeting,
            pings_to_names = pings_to_names
        ),
        view = build_confirmation_view(
            meetings = meetings,
            pings_to_names = pings_to_names,
            target_meeting = target_meeting
        )
    )


# ON MEETING SELECT

async def on_meeting_select(
    interaction: Interaction,
    meetings: list[Meeting],
    target_meeting: Meeting
) -> None:
    # Confirmation.
    print('In on meeting select, sending confirmation view.')

    pings_to_names = get_pings_to_names(interaction.guild)

    await interaction.response.edit_message(
        content = build_confirmation_content(
            target_meeting = target_meeting,
            pings_to_names = pings_to_names
        ),
        view = build_confirmation_view(
            meetings = meetings,
            pings_to_names = pings_to_names,
            target_meeting = target_meeting
        )
    )


# CONFIRMATION

async def on_confirm(
    interaction: Interaction,
    meetings: list[Meeting],
    pings_to_names: dict[str: str],
    target_meeting: Meeting,
    **_
) -> None:
    print('In on confirm, getting target meeting.')

    title = target_meeting.get_title(True)

    if not target_meeting in meetings:
        interaction.response.edit_message(
            content = (
                f'It seems {title} does not exist at the time of confirmation. 🧐\n'
                'No status to toggle.'
            ),
            view = None
        )
        print('Nonexistent target meeting, terminating.')
        return
    
    new_active = target_meeting.toggle_active()
    save_meetings()
    print('Active status on target meeting toggled, data saved.')

    output = (
        f'{title} has been __{(
            'activated__! 🔊' if new_active else 'deactivated__! 🔇'
        )}\n'
        f'{target_meeting.to_discord(pings_to_names = pings_to_names)}\n\n'
        f'{'Let\'s do this! 🫡' if new_active else 'Take a breather! 😙'}'
    )

    await interaction.message.edit(content = output, view = None)

    await interaction.client.get_channel(int(getenv(GETENV_NOTIFY_CHANNEL_ID))).send(
        content = f'{output}\n{' '.join(target_meeting.get_participants())}',
        view = None
    )

    failed_dm_users = await dm_users_from_pings(
        bot = interaction.client,
        pings = target_meeting.get_dm(),
        pings_to_names = pings_to_names,
        message = (
            f'Letting you know that a meeting you\'re in has been **{(
                'activated' if new_active else 'deactivated'
            )}**:\n'
            f'{target_meeting.to_discord(pings_to_names = pings_to_names)}\n\n'
            f'{'Let\'s do this! 🫡' if new_active else 'Take a breather! 😙'}'
        )
    )

    if failed_dm_users: await interaction.followup.send(
        build_failed_dm_err(failed_dm_users)
    )
    print('DMs have been sent.')

    print('Toggle active command end, confirmed.')

async def on_cancel(
    interaction: Interaction,
    target_meeting: Meeting,
    **_
) -> None:
    print('In on cancel.')

    title = target_meeting.get_title(True)

    await interaction.response.edit_message(
        content = (
            f'{title} will __remain {(
                'active! 🔊' if target_meeting.get_active() else 'inactive! 🔇'
            )}__'
        ),
        view = None
    )

    print('Toggle active command end, cancelled.')


def build_confirmation_content(
    target_meeting: Meeting,
    pings_to_names: dict[str: str]
) -> str:
    if target_meeting.get_active():
        return (
            f'Target meeting is **currently active**:\n'
            f'{target_meeting.to_discord(pings_to_names = pings_to_names)}\n\n'
            'Would you like to **deactivate** this meeting? (Will not notify)'
        )
    
    return (
        f'Target meeting is **currently inactive**:\n'
        f'{target_meeting.to_discord(pings_to_names = pings_to_names)}\n\n'
        'Would you like to **activate** this meeting? (Will notify)'
    )

def build_confirmation_view(
    meetings: list[Meeting],
    pings_to_names: dict[str: str],
    target_meeting: Meeting
) -> ConfirmationViewDefault:
    return ConfirmationViewDefault(
        on_confirm = on_confirm,
        on_cancel = on_cancel,
        meetings = meetings,
        pings_to_names = pings_to_names,
        target_meeting = target_meeting
    )
