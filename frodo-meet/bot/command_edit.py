'''Frodo Meet - Edit Meeting Command
'''
from discord import Interaction, SelectOption
from discord.ui import View, Select

from copy import deepcopy

from common.util import (
    get_response,
    ConfirmationViewDefault,
    RESPONSE_TIMEOUT,
    NULL_SELECT_VALUE,
)

from frodo_meet_helper import (
    get_meetings_to_discord,
    find_meeting,
    add_meeting,
    remove_meeting,
    is_title_taken,
    parse_participants,
)
from frodo_meet_discord_views import MeetingSelectView, RecurrenceSelectView
from frodo_meet_data import save_meetings
from meeting import (Meeting,
    ATTRIBUTE_TITLE,
    ATTRIBUTE_TIME,
    ATTRIBUTE_DESCRIPTION,
    ATTRIBUTE_PARTICIPANTS,
    ATTRIBUTE_DM,
    ATTRIBUTE_RECURRENCE,
)
from meeting_time import MeetingTime


async def edit_meeting(
    interaction: Interaction,
    meetings: list[Meeting],
    ids_to_names: dict[str: str],
    target: str
) -> None:
    print('Edit meeting command start.')

    if not meetings:
        await interaction.response.send_message('There are no meetings to edit. 🧐')
        print('No meetings, terminating.')
        return
    
    # STEP 1: If no target arg was given, go to meeting select.
    if not target:
        print('No target string, sending meeting select view.')

        await interaction.response.send_message(
            content = (
                f'Enter the title or index of the meeting you want to delete:\n'
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
    
    # STEP 2: Get property to edit.
    print('Got target meeting, sending edit property select view.')

    await interaction.response.send_message(
        content = build_on_meeting_select_content(target_meeting),
        view = EditPropertySelectView(meetings, ids_to_names, target_meeting)
    )


# ON MEETING SELECT

async def on_meeting_select(
    interaction: Interaction,
    meetings: list[Meeting],
    target_meeting: Meeting,
    ids_to_names: dict[str: str]
) -> None:
    # STEP 2: Get property to edit.
    print('In on meeting select, sending edit property select view.')

    await interaction.response.edit_message(
        content = build_on_meeting_select_content(target_meeting),
        view = EditPropertySelectView(meetings, target_meeting, ids_to_names)
    )

def build_on_meeting_select_content(target_meeting: Meeting) -> str:
    return (
        f'You are editing {target_meeting.get_title(True)}.\n'
        'Which property would you like to edit?'
    )


# EDIT PROPERTY SELECT

class EditPropertySelectView(View):
    def __init__(self,
        meetings: list[Meeting],
        target_meeting: Meeting,
        ids_to_names: dict[str: str]
    ) -> None:
        print('In edit property select view, awaiting target property select…')
        super().__init__(timeout = RESPONSE_TIMEOUT)
        self.add_item(EditPropertySelect(meetings, target_meeting, ids_to_names))

class EditPropertySelect(Select):
    _meetings: list[Meeting]
    _target_meeting: Meeting
    _ids_to_names: dict[str: str]

    def __init__(self,
        meetings: list[Meeting],
        target_meeting: Meeting,
        ids_to_names: dict[str: str]
    ) -> None:
        self._meetings = meetings
        self._target_meeting = target_meeting
        self._ids_to_names = ids_to_names

        super().__init__(
            placeholder = 'Select property…',
            options = [
                SelectOption(label = ATTRIBUTE_TITLE.capitalize(), value = ATTRIBUTE_TITLE),
                SelectOption(label = ATTRIBUTE_TIME.capitalize(), value = ATTRIBUTE_TIME),
                SelectOption(label = ATTRIBUTE_DESCRIPTION.capitalize(), value = ATTRIBUTE_DESCRIPTION),
                SelectOption(label = ATTRIBUTE_PARTICIPANTS.capitalize(), value = ATTRIBUTE_PARTICIPANTS),
                SelectOption(label = ATTRIBUTE_DM.capitalize(), value = ATTRIBUTE_DM),
                SelectOption(label = ATTRIBUTE_RECURRENCE.capitalize(), value = ATTRIBUTE_RECURRENCE)
            ]
        )
    
    async def callback(self, interaction: Interaction) -> None:
        print('Target property selected.')
        target_property = self.values[0]

        meetings = self._meetings
        ids_to_names = self._ids_to_names
        target_meeting = self._target_meeting

        # Deepcopy target meeting for preview of changes.
        updated_meeting = deepcopy(target_meeting)

        # STEP 3: Get new value.
        # If editing recurrence, go to recurrence select view.
        if target_property == ATTRIBUTE_RECURRENCE:
            print('Editing recurrence, sending recurrence select view.')

            await interaction.response.edit_message(
                content = (
                    f'You are editing the __{target_property}__ of {target_meeting.get_title(True)}.\n'
                    'Please select the new recurrence.\n'
                    'For a one-time meeting, select *Normal (one-time)*.'
                ),
                view = RecurrenceSelectView(
                    on_select = on_recurrence_select,
                    meetings = meetings,
                    ids_to_names = ids_to_names,
                    target_meeting = target_meeting,
                    updated_meeting = updated_meeting
                )
            )
            return

        # Otherwise, await new value as a response.
        print('Awaiting new value…')

        await interaction.response.edit_message(
            content = (
                f'You are editing the __{target_property}__ of {target_meeting.get_title(True)}.\n'
                'Please enter the new value *as you would when creating a new meeting*.'
            ),
            view = None
        )
        
        new_value_message = await get_response(interaction)
        print('Got new value.')

        # If editing title:
        if target_property == ATTRIBUTE_TITLE:
            print('Editing title.')

            title = new_value_message.content
            taken_err = is_title_taken(meetings, title)

            # If title is taken, send error message and terminate.
            if taken_err:
                await interaction.followup.send(taken_err)
                print('Title taken error, terminating.')
                return
            
            updated_meeting.set_title(title)

        # If editing time:
        if target_property == ATTRIBUTE_TIME:
            print('Editing time.')

            time = MeetingTime.from_input(new_value_message.content)

            if isinstance(time, str):
                await interaction.followup.send(time)
                print('Time error, terminating.')
                return
            
            updated_meeting.set_time(time)

            # Reset meeting's soon status.
            updated_meeting.set_soon()
        
        # If editing participants:
        elif target_property == ATTRIBUTE_PARTICIPANTS:
            print('Editing participants.')
            participants = parse_participants(new_value_message)
            updated_meeting.set_participants(participants)
        
        # If editing pings by dm:
        elif target_property == ATTRIBUTE_DM:
            print('Editing pings by dm.')
            pingsbydm = parse_participants(new_value_message)
            updated_meeting.set_dm(pingsbydm)
        
        # Otherwise, editing description:
        else:
            print('Editing description.')
            description = new_value_message.content
            updated_meeting.set_description(description)

        # STEP 4: Confirmation.
        print('New value set on updated meeting, sending confirmation view.')

        await interaction.followup.send(
            content = build_confirmation_content(updated_meeting, ids_to_names),
            view = build_confirmation_view(meetings, target_meeting, updated_meeting)
        )


# ON RECURRENCE SELECT

async def on_recurrence_select(
    interaction: Interaction,
    recurrence: str,
    meetings: list[Meeting],
    ids_to_names: dict[str: str],
    target_meeting: Meeting,
    updated_meeting: Meeting,
    **_
) -> None:
    print('In on recurrence select.')

    # Set recurrence.
    updated_meeting.set_recurrence(recurrence if recurrence != NULL_SELECT_VALUE else '')

    # STEP 4: Confirmation.
    print('New value set on updated meeting, sending confirmation view.')

    await interaction.response.edit_message(
        content = build_confirmation_content(updated_meeting, ids_to_names),
        view = build_confirmation_view(meetings, target_meeting, updated_meeting)
    )


# CONFIRMATION

async def on_confirm(
    interaction: Interaction,
    meetings: list[Meeting],
    target_meeting: Meeting,
    updated_meeting: Meeting,
    **_
) -> None:
    print('In on confirm, removing original meeting.')

    # Remove original meeting.
    remove_err = remove_meeting(meetings, target_meeting)
    if remove_err:
        await interaction.response.edit_message(
            content = f'{remove_err}\nNothing to edit.',
            view = None
        )
        print('Remove error, terminating.')
        return
    
    # Add updated meeting.
    add_meeting(meetings, updated_meeting)
    save_meetings()
    print('Updated meeting added, data saved.')

    await interaction.response.edit_message(
        content = f'Changes to {target_meeting.get_title(True)} have been __saved__! ✨',
        view = None
    )

    print('Edit meeting command end, confirmed.')

async def on_cancel(
    interaction: Interaction,
    target_meeting: Meeting,
    **_
) -> None:
    print('In on cancel.')

    await interaction.response.edit_message(
        content = f'Changes for {target_meeting.get_title(True)} have been __discarded__! 🗑️',
        view = None
    )

    print('Edit meeting command end, cancelled.')


def build_confirmation_content(
    updated_meeting: Meeting,
    ids_to_names: dict[str: str]
) -> str:
    return (
        'Updated meeting:\n'
        f'{updated_meeting.to_discord(full = True, ids_to_names = ids_to_names,)}\n\n'
        'Would you like to save these changes?'
    )

def build_confirmation_view(
    meetings: list[Meeting],
    target_meeting: Meeting,
    updated_meeting: Meeting
) -> ConfirmationViewDefault:
    return ConfirmationViewDefault(
        on_confirm = on_confirm,
        on_cancel = on_cancel,
        timeout = RESPONSE_TIMEOUT,
        meetings = meetings,
        target_meeting = target_meeting,
        updated_meeting = updated_meeting
    )
