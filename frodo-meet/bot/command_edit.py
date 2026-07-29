'''Frodo Meet - Edit Meeting Command
'''
from discord import Interaction, SelectOption
from discord.ui import View, Select

from os import getenv
from copy import deepcopy

from common.util import (
    get_response,
    parse_input,
    ConfirmationViewDefault,
    get_pings_to_names,
    dm_users_from_pings,
    RESPONSE_TIMEOUT,
    NULL_SELECT_VALUE,
)

from frodo_meet_helper import (
    get_meetings_to_discord,
    find_meeting,
    add_meeting,
    remove_meeting,
    is_title_taken,
    get_names_to_pings,
    verify_names,
    build_failed_dm_err,
)
from frodo_meet_data import save_meetings, GETENV_NOTIFY_CHANNEL_ID
from frodo_meet_discord_views import MeetingSelectView, RecurrenceSelectView
from meeting import (Meeting,
    ATTRIBUTE_TITLE,
    ATTRIBUTE_TIME,
    ATTRIBUTE_DESCRIPTION,
    ATTRIBUTE_PARTICIPANTS,
    ATTRIBUTE_DM,
    ATTRIBUTE_RECURRENCE,
    PARTICIPANTS_BREAKPOINTS,
)
from meeting_time import MeetingTime

PARTICIPANTS_ADD = 'Add Participants'
PARTICIPANTS_REMOVE = 'Remove Participants'
DM_ADD = 'Add pings by DM'
DM_REMOVE = 'Remove pings by DM'


async def edit_meeting(
    interaction: Interaction,
    meetings: list[Meeting],
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
                f'{get_meetings_to_discord(interaction, meetings, ('all',))}'
            ),
            view = MeetingSelectView(
                on_select = on_meeting_select,
                meetings = meetings
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
        view = EditPropertySelectView(
            meetings = meetings,
            target_meeting = target_meeting
        )
    )


# ON MEETING SELECT

async def on_meeting_select(
    interaction: Interaction,
    meetings: list[Meeting],
    target_meeting: Meeting
) -> None:
    # STEP 2: Get property to edit.
    print('In on meeting select, sending edit property select view.')

    await interaction.response.edit_message(
        content = build_on_meeting_select_content(target_meeting),
        view = EditPropertySelectView(
            meetings = meetings,
            target_meeting = target_meeting
        )
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
        target_meeting: Meeting
    ) -> None:
        print('In edit property select view, awaiting target property select…')
        super().__init__(timeout = RESPONSE_TIMEOUT)
        self.add_item(EditPropertySelect(
            meetings = meetings,
            target_meeting = target_meeting
        ))

class EditPropertySelect(Select):
    _meetings: list[Meeting]
    _target_meeting: Meeting

    def __init__(self,
        meetings: list[Meeting],
        target_meeting: Meeting
    ) -> None:
        self._meetings = meetings
        self._target_meeting = target_meeting

        super().__init__(
            placeholder = 'Select property…',
            options = [
                SelectOption(label = ATTRIBUTE_TITLE.capitalize(), value = ATTRIBUTE_TITLE),
                SelectOption(label = ATTRIBUTE_TIME.capitalize(), value = ATTRIBUTE_TIME),
                SelectOption(label = ATTRIBUTE_DESCRIPTION.capitalize(), value = ATTRIBUTE_DESCRIPTION),
                SelectOption(label = PARTICIPANTS_ADD, value = PARTICIPANTS_ADD),
                SelectOption(label = PARTICIPANTS_REMOVE, value = PARTICIPANTS_REMOVE),
                SelectOption(label = DM_ADD, value = DM_ADD),
                SelectOption(label = DM_REMOVE, value = DM_REMOVE),
                SelectOption(label = ATTRIBUTE_RECURRENCE.capitalize(), value = ATTRIBUTE_RECURRENCE),
            ]
        )
    
    async def callback(self, interaction: Interaction) -> None:
        print('Target property selected.')
        target_property = self.values[0]

        meetings = self._meetings
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
                    target_meeting = target_meeting,
                    updated_meeting = updated_meeting,
                    target_property = target_property
                )
            )
            return

        # Otherwise, await new value as a response.
        print('Awaiting new value…')

        await interaction.response.edit_message(
            content = (
                f'You are editing the __{build_target_property_content(target_property)}__ of {target_meeting.get_title(True)}.\n'
                'Please enter the new value *as you would when creating a new meeting*.'
            ),
            view = None
        )
        
        new_value_input = await get_response(interaction)
        print('Got new value.')

        new_pings = []
        names_to_pings = get_names_to_pings(interaction.guild)

        # If editing title:
        if target_property == ATTRIBUTE_TITLE:
            print('Editing title.')

            title = new_value_input.content
            taken_err = is_title_taken(meetings, title)

            # If title is taken, send error message and terminate.
            if taken_err:
                await interaction.followup.send(taken_err)
                print('Title taken error, terminating.')
                return
            
            updated_meeting.set_title(title)

        # If editing time:
        elif target_property == ATTRIBUTE_TIME:
            print('Editing time.')

            time = MeetingTime.from_input(new_value_input.content)

            if isinstance(time, str):
                await interaction.followup.send(time)
                print('Time error, terminating.')
                return
            
            updated_meeting.set_time(time)

            # Reset meeting's soon status.
            updated_meeting.set_soon()
        
        # If editing description:
        elif target_property == ATTRIBUTE_DESCRIPTION:
            print('Editing description.')
            updated_meeting.set_description(new_value_input.content)
        
        # If adding participants:
        elif target_property == PARTICIPANTS_ADD:
            print('Adding participants.')
            new_pings = [names_to_pings[name] for name in verify_names(
                parse_input(new_value_input.content, PARTICIPANTS_BREAKPOINTS),
                names_to_pings
            )]
            updated_meeting.add_pings(new_pings, ATTRIBUTE_PARTICIPANTS)
        
        # If removing participants:
        elif target_property == PARTICIPANTS_REMOVE:
            print('Removing participants.')
            new_pings = [names_to_pings[name] for name in parse_input(
                new_value_input.content, PARTICIPANTS_BREAKPOINTS
            )]
            updated_meeting.remove_pings(new_pings, ATTRIBUTE_PARTICIPANTS)
        
        # If adding pings by dm:
        elif target_property == DM_ADD:
            print('Adding pings by dm.')
            new_pings = [names_to_pings[name] for name in verify_names(
                parse_input(new_value_input.content, PARTICIPANTS_BREAKPOINTS),
                names_to_pings
            )]
            updated_meeting.add_pings(new_pings, ATTRIBUTE_DM)
        
        # If removing pings by dm:
        elif target_property == DM_REMOVE:
            print('Removing pings by dm.')
            new_pings = [names_to_pings[name] for name in parse_input(
                new_value_input.content, PARTICIPANTS_BREAKPOINTS
            )]
            updated_meeting.remove_pings(new_pings, ATTRIBUTE_DM)
        
        # Otherwise, unkown target property.
        else:
            print('Unknown target property, terminating.')
            return

        # STEP 4: Confirmation.
        print('New value set on updated meeting, sending confirmation view.')

        pings_to_names = get_pings_to_names(interaction.guild)

        await interaction.followup.send(
            content = build_confirmation_content(
                updated_meeting = updated_meeting,
                pings_to_names = pings_to_names
            ),
            view = build_confirmation_view(
                meetings = meetings,
                pings_to_names = pings_to_names,
                target_meeting = target_meeting,
                updated_meeting = updated_meeting,
                target_property = target_property,
                updated_names = new_pings
            )
        )


def build_target_property_content(target_property: str) -> str:
    return (
        target_property if target_property not in (
            PARTICIPANTS_ADD, PARTICIPANTS_REMOVE, DM_ADD, DM_REMOVE
        ) else
        
        ATTRIBUTE_PARTICIPANTS if target_property in (
            PARTICIPANTS_ADD, PARTICIPANTS_REMOVE
        ) else
        
        'pings by DM'
    )


# ON RECURRENCE SELECT

async def on_recurrence_select(
    interaction: Interaction,
    meetings: list[Meeting],
    recurrence: str,
    target_meeting: Meeting,
    updated_meeting: Meeting,
    target_property: str,
    **_
) -> None:
    print('In on recurrence select.')

    # Set recurrence.
    updated_meeting.set_recurrence(recurrence if recurrence != NULL_SELECT_VALUE else '')

    # STEP 4: Confirmation.
    print('New value set on updated meeting, sending confirmation view.')

    pings_to_names = get_pings_to_names(interaction.guild)

    await interaction.response.edit_message(
        content = build_confirmation_content(
            updated_meeting = updated_meeting,
            pings_to_names = pings_to_names
        ),
        view = build_confirmation_view(
            meetings = meetings,
            pings_to_names = pings_to_names,
            target_meeting = target_meeting,
            updated_meeting = updated_meeting,
            target_property = target_property
        )
    )


# CONFIRMATION

async def on_confirm(
    interaction: Interaction,
    meetings: list[Meeting],
    target_meeting: Meeting,
    updated_meeting: Meeting,
    target_property: str,
    updated_pings: list[str] = [],
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

    pings_to_names = get_pings_to_names(interaction.guild)

    output = (
        f'Changes for the {build_target_property_content(target_property)} for {target_meeting.get_title(True)} have been __saved__! ✨\n'
        f'{updated_meeting.to_discord(pings_to_names = pings_to_names)}'
    )

    await interaction.message.edit(content = output, view = None)

    await interaction.client.get_channel(int(getenv(GETENV_NOTIFY_CHANNEL_ID))).send(
        content = (
            f'{output}'
            f'{(
                f'\n\n{' '.join(updated_meeting.get_participants())}'
                if target_property == ATTRIBUTE_TIME else
    
                f'\n\n{' '.join(updated_pings)}'
                if updated_pings else
    
                ''
            )}'
        ), view = None
    )

    failed_dm_users = await dm_users_from_pings(
        bot = interaction.client,
        pings = (
            updated_meeting.get_dm()
            if target_property == ATTRIBUTE_TIME else

            [ping for ping in updated_pings if ping in updated_meeting.get_dm()]
            if target_property in (PARTICIPANTS_ADD, PARTICIPANTS_REMOVE) else

            updated_pings
            if target_property in (DM_ADD, DM_REMOVE) else

            []
        ),
        pings_to_names = pings_to_names,
        message = (
            f'Letting you know that {(
                'the **time for a meeting you\'re in has changed**'
                if target_property == ATTRIBUTE_TIME else

                'you\'ve been **added to a meeting**'
                if target_property == PARTICIPANTS_ADD else

                'you\'ve been **removed from a meeting**'
                if target_property == PARTICIPANTS_REMOVE else

                'you\'ve been **added to the list of pings by DM** for a meeting'
                if target_property == DM_ADD else

                'you\'ve been **removed from the list of pings by DM** for a meeting'
            )}:\n'
            f'{updated_meeting.to_discord(
                pings_to_names = pings_to_names
                if target_property in (ATTRIBUTE_TIME, PARTICIPANTS_ADD, DM_ADD)
                else None
            )}'
        )
    )

    if failed_dm_users: await interaction.followup.send(
        build_failed_dm_err(failed_dm_users)
    )
    print('DMs have been sent.')

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
    pings_to_names: dict[str: str]
) -> str:
    return (
        'Updated meeting:\n'
        f'{updated_meeting.to_discord(pings_to_names = pings_to_names)}\n\n'
        'Would you like to save these changes?'
    )

def build_confirmation_view(
    meetings: list[Meeting],
    pings_to_names: dict[str: str],
    target_meeting: Meeting,
    updated_meeting: Meeting,
    target_property: str,
    updated_names: list[str] = []
) -> ConfirmationViewDefault:
    return ConfirmationViewDefault(
        on_confirm = on_confirm,
        on_cancel = on_cancel,
        meetings = meetings,
        pings_to_names = pings_to_names,
        target_meeting = target_meeting,
        updated_meeting = updated_meeting,
        target_property = target_property,
        updated_names = updated_names
    )
