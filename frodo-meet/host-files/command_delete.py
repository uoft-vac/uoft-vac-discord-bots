'''Frodo Meet - Delete Meeting Command
'''
from discord import Interaction

from common.common_bot_helper import ConfirmationViewDefault

from frodo_meet_helper import get_meetings_to_discord, find_meeting, remove_meeting
from frodo_meet_discord_views import MeetingSelectView
from frodo_meet_data import save_meetings

from meeting import Meeting


async def delete_meeting(
    interaction: Interaction,
    meetings: list[Meeting],
    ids_to_names: dict[str: str],
    target: str
) -> None:
    print('Delete meeting command start.')

    if not meetings:
        await interaction.response.send_message('There are no meetings to delete. 🧐')
        print('No meetings, terminating,')
        return
    
    # If no target arg was given, go to meeting select.
    if not target:
        print('No target string, sending meeting select view.')

        await interaction.response.send_message(
            content = (
                f'Enter the title or index of the meeting you want to delete:\n'
                f'{get_meetings_to_discord(('all',), meetings, None)}'
            ),
            view = MeetingSelectView(
                on_meeting_select,
                meetings,
                ids_to_names
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
        content = build_confirmation_content(ids_to_names, target_meeting),
        view = build_confirmation_view(meetings, target_meeting)
    )


# ON MEETING SELECT

async def on_meeting_select(
    interaction: Interaction,
    meetings: list[Meeting],
    ids_to_names: dict[str: str],
    target_meeting: Meeting
) -> None:
    # Confirmation.
    print('In on meeting select, sending confirmation view.')

    await interaction.response.edit_message(
        content = build_confirmation_content(ids_to_names, target_meeting),
        view = build_confirmation_view(meetings, target_meeting)
    )


# CONFIRMATION

async def on_confirm(
    interaction: Interaction,
    meetings: list[Meeting],
    target_meeting: Meeting,
    **_
) -> None:
    print('In on confirm, removing target meeting.')

    remove_err = remove_meeting(meetings, target_meeting)
    if remove_err:
        await interaction.response.edit_message(
            content = f'{remove_err}\nNothing to delete.',
            view = None
        )
        print('Remove error, terminating.')
        return
    
    save_meetings()
    print('Target meeting removed, data saved.')

    await interaction.response.edit_message(
        content = f'{target_meeting.get_title(True)} has been deleted! 💥',
        view = None
    )
    
    print('Delete meeting command end, confirmed.')

async def on_cancel(
    interaction: Interaction,
    target_meeting: Meeting,
    **_
) -> None:
    print('In on cancel.')

    await interaction.response.edit_message(
        content = f'{target_meeting.get_title(True)} was spared! 😇',
        view = None
    )

    print('Delete meeting command end, cancelled.')


def build_confirmation_content(ids_to_names: dict[str: str], target_meeting: Meeting) -> str:
    return (
        'Target meeting:\n'
        f'{target_meeting.to_discord(full = True, ids_to_names = ids_to_names,)}\n\n'
        'Would you like to delete this meeting?'
    )

def build_confirmation_view(meetings: list[Meeting], target_meeting: Meeting) -> ConfirmationViewDefault:
    return ConfirmationViewDefault(
        on_confirm = on_confirm,
        on_cancel = on_cancel,
        meetings = meetings,
        target_meeting = target_meeting
    )
