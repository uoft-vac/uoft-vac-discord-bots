'''Frodo Meet - Toggle Active Command
'''
from discord import Interaction

from common.util import ConfirmationViewDefault

from frodo_meet_helper import (
    get_meetings_to_discord,
    find_meeting,
    dm_meeting,
    build_failed_dm_err,
)
from frodo_meet_discord_views import MeetingSelectView
from frodo_meet_data import save_meetings
from meeting import Meeting


async def toggle_active(
    interaction: Interaction,
    meetings: list[Meeting],
    ids_to_names: dict[str: str],
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
                f'{get_meetings_to_discord(meetings, None, ('all',))}'
            ),
            view = MeetingSelectView(
                on_meeting_select,
                meetings,
                ids_to_names = ids_to_names
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
    await interaction.response.send_message(
        content = build_confirmation_content(target_meeting),
        view = build_confirmation_view(meetings, target_meeting, ids_to_names)
    )


# ON MEETING SELECT

async def on_meeting_select(
    interaction: Interaction,
    meetings: list[Meeting],
    target_meeting: Meeting,
    ids_to_names: dict[str: str]
) -> None:
    # Confirmation.
    print('In on meeting select, sending confirmation view.')
    await interaction.response.edit_message(
        content = build_confirmation_content(target_meeting),
        view = build_confirmation_view(meetings, target_meeting, ids_to_names)
    )


# CONFIRMATION

async def on_confirm(
    interaction: Interaction,
    meetings: list[Meeting],
    target_meeting: Meeting,
    ids_to_names: dict[str: str],
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

    await interaction.response.edit_message(
        content = (
            f'{title} has been __{(
                'activated__! 🔊' if new_active else 'deactivated__! 🔇'
            )}\n'
            f'{'Let\'s do this! 🫡' if new_active else 'Take a breather! 😙'}\n'
            f'{' '.join(target_meeting.get_participants())}'
        ),
        view = None
    )

    failed_dm_users = await dm_meeting(interaction.client, target_meeting, (
        f'Letting you know that a meeting you\'re in has been **{(
            'activated' if new_active else 'deactivated'
        )}**:\n'
        f'{target_meeting.to_discord(full = True, ids_to_names = ids_to_names)}\n\n'
        f'{'Let\'s do this! 🫡' if new_active else 'Take a breather! 😙'}'
    ), ids_to_names)

    if failed_dm_users: await interaction.followup.send(
        build_failed_dm_err(failed_dm_users, ids_to_names)
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


def build_confirmation_content(target_meeting: Meeting, ids_to_names: dict[str:str]) -> str:
    if target_meeting.get_active():
        return (
            f'Target meeting is currently __active__:\n'
            f'{target_meeting.to_discord(full = True, ids_to_names = ids_to_names,)}\n\n'
            'Would you like to __deactivate__ this meeting? (Will not notify)'
        )
    
    return (
        f'Target meeting is currently __inactive__:\n'
        f'{target_meeting.to_discord(full = True, ids_to_names = ids_to_names,)}\n\n'
        'Would you like to __activate__ meeting? (Will notify)'
    )

def build_confirmation_view(
    meetings: list[Meeting],
    target_meeting: Meeting,
    ids_to_names: dict[str: str]
) -> ConfirmationViewDefault:
    return ConfirmationViewDefault(
        on_confirm = on_confirm,
        on_cancel = on_cancel,
        meetings = meetings,
        target_meeting = target_meeting,
        ids_to_names = ids_to_names
    )
