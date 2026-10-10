'''Frodo Meet

UofT Visual Arts Club exec team's Discord bot for easy meeting plan management.

Can create and manage meeting with Discord commands.
Also notifies meeting members when a meeting is about to start.
Stores and reads meeting data in meetings_data.json.

Driver file.
'''
greet_on_boot = True # Toggleable
greet_str = 'Frodomeet clocking in from **Sunny\'s machine**! 🌞'

from discord import Intents, Interaction, TextChannel
from discord.ext import commands

from asyncio import sleep
from os import getcwd, getenv

from common.env import load_local_dotenv, GETENV_BOT_TOKEN
from common.output import chop_output, restrict_to_channel
from common.discord_id import get_pings_to_names
from common.misc import DIVIDER_STR

from frodo_meet_data import (
    load_meetings,
    get_meetings,
    save_meetings,
    GETENV_COMMANDS_CHANNEL_ID,
    GETENV_NOTIFY_CHANNEL_ID,
)
from meeting_time import MeetingTime
import command_show, command_create, command_delete, command_edit, command_toggle_active, command_help
from frodo_meet_background_tasks import notify_meetings_relative, begin_meetings, dm_notifications

CHECK_INTERVAL_SECS = 60 # Seconds between each check for meetings to notify/begin.
NOTICE_TIME_INIT_SECS = 3 * 60 * 60 # 3 hours
NOTICE_TIME_SOON_SECS = 5 * 60 # 5 mins


# SETUP

intents = Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix = '.', intents = intents)
tree = bot.tree
command = tree.command

background_task = None

@bot.event
async def on_ready():
    global background_task

    load_meetings()

    await tree.sync()
    print(f'Logged in as {bot.user}.')

    if greet_on_boot:
        await bot.get_channel(
            int(getenv(GETENV_COMMANDS_CHANNEL_ID))
        ).send(greet_str)

    if background_task is not None:
        print('Background task already exists. 🧐')
        return

    print('Beginning background task.')
    background_task = bot.loop.create_task(auto_notify_n_begin(
        bot.get_channel(int(getenv(GETENV_NOTIFY_CHANNEL_ID)))
    ))


# COMMANDS

@command(
    name = 'show-meetings',
    description = 'Display recorded meeting plans.'
)
async def show_meetings(interaction: Interaction, filters: str = '') -> None:
    if not await restrict_to_channel(interaction,
        bot.get_channel(int(getenv(GETENV_COMMANDS_CHANNEL_ID)))
    ): return

    print(
        f'{DIVIDER_STR}\n'
        f'Show meetings command prompted, calling command.'
    )
    await command_show.show_meetings(
        interaction = interaction,
        meetings = get_meetings(),
        filters = filters
    )


@command(
    name = 'create-meeting',
    description = 'Create a new meeting!'
)
async def create_meeting(interaction: Interaction) -> None:
    if not await restrict_to_channel(interaction,
        bot.get_channel(int(getenv(GETENV_COMMANDS_CHANNEL_ID)))
    ): return
    
    print(
        f'{DIVIDER_STR}\n'
        f'Create meeting command prompted, calling command.'
    )
    await command_create.create_meeting(
        interaction = interaction,
        meetings = get_meetings()
    )


@command(
    name = 'delete-meeting',
    description = 'Delete an existing meeting!'
)
async def delete_meeting(interaction: Interaction, target: str = None) -> None:
    if not await restrict_to_channel(interaction,
        bot.get_channel(int(getenv(GETENV_COMMANDS_CHANNEL_ID)))
    ): return

    print(
        f'{DIVIDER_STR}\n'
        f'Delete meeting command prompted, calling command.'
    )
    await command_delete.delete_meeting(
        interaction = interaction,
        meetings = get_meetings(),
        target = target
    )


@command(
    name = 'edit-meeting',
    description = 'Edit a property for an existing meeting!'
)
async def edit_meeting(interaction: Interaction, target: str = None) -> None:
    if not await restrict_to_channel(interaction,
        bot.get_channel(int(getenv(GETENV_COMMANDS_CHANNEL_ID)))
    ): return

    print(
        f'{DIVIDER_STR}\n'
        f'Edit meeting command prompted, calling command.'
    )
    await command_edit.edit_meeting(
        interaction = interaction,
        meetings = get_meetings(),
        target = target
    )


@command(
    name = 'toggle-active',
    description = 'Activate an inactive meeting, or deactivate an active meeting!'
)
async def toggle_active(interaction: Interaction, target: str = None) -> None:
    if not await restrict_to_channel(interaction,
        bot.get_channel(int(getenv(GETENV_COMMANDS_CHANNEL_ID)))
    ): return

    print(
        f'{DIVIDER_STR}\n'
        f'Toggle active command prompted, calling command.'
    )
    await command_toggle_active.toggle_active(
        interaction = interaction,
        meetings = get_meetings(),
        target = target
    )


@command(
    name = 'help',
    description = 'Need help? I got you!'
)
async def help(interaction: Interaction) -> None:
    if not await restrict_to_channel(interaction,
        bot.get_channel(int(getenv(GETENV_COMMANDS_CHANNEL_ID)))
    ): return

    print(
        f'{DIVIDER_STR}\n'
        f'Help command prompted, calling command.'
    )
    await command_help.help(
        interaction
    )


# BACKGROUND TASKS

async def auto_notify_n_begin(notify_channel: TextChannel) -> None:
    '''
    Every specified interval:
    1. Check if there are any meetings that are about to start, given a timeframe.
    2. Check if there are any meetings that have begun (meeting time is past current time).
    If these are true, print the appropriate output(s) in the notify channel.
    '''
    print('In auto notify n begin, beginning loop.')

    # Loop as long as bot is online.
    while not bot.is_closed():
        print(DIVIDER_STR)
        # await notify_channel.send(f'Test: the current time is {MeetingTime.get_now().to_discord()}.')

        meetings = get_meetings()
        now = MeetingTime.get_now()
        pings_to_names = get_pings_to_names(notify_channel.guild)

        # Check for any meetings to notify initially and get the output.
        notify_output_init, to_dm = notify_meetings_relative(
            meetings = meetings,
            now = now,
            notice_time_secs = NOTICE_TIME_INIT_SECS
        )
        print('Got notify init result.')

        # Check for any meetings to notify soon and get the output.
        notify_output_soon, _ = notify_meetings_relative(
            meetings = meetings,
            now = now,
            notice_time_secs = NOTICE_TIME_SOON_SECS,
            target_notify_status = 1
        )
        print('Got notify soon result.')

        # Check for any meetings to begin and get the output.
        begin_output = begin_meetings(meetings = meetings, now = now)
        print('Got begin results.')

        # If meetings are modified, save data.
        if notify_output_init or notify_output_soon or begin_output:
            save_meetings()
            print('Meetings data saved.')

        # If there are meetings that have begun, print it in the auto channel.
        if begin_output:
            for suboutput in chop_output('\n'.join([meeting_data[1] for meeting_data in begin_output])):
                await notify_channel.send(suboutput)
            print('Meetings have begun!')
        else: print('No meetings to begin.')

        # Clear entries in output init and soon that have begun to prevent redundant outputs.
        notify_output_init = [
            (meeting_no, to_dm_) for meeting_no, to_dm_ in notify_output_init
            if meeting_no not in [meeting_bo for meeting_bo, _ in begin_output]
        ]
        notify_output_soon = [
            (meeting_no, to_dm_) for meeting_no, to_dm_ in notify_output_soon
            if meeting_no not in [meeting_bo for meeting_bo, _ in begin_output]
        ]

        # If there are meetings to notify soon, print it in the auto channel.
        if notify_output_soon:
            print('Sending soon notify…')

            for suboutput in chop_output(
                'The following meeting(s) will begin soon:\n'
                f'{'\n'.join([
                    f'{(meeting_data[0].get_title(True))} {' '.join(meeting_data[0].get_participants())}'
                    for meeting_data in notify_output_soon
                ])}'
            ): await notify_channel.send(suboutput)

            print('Soon notified!')
        else: print('No soon to notify.')

        # Clear entries in output init that have been notified to prevent redundant outputs.
        notify_output_init = [
            (meeting_noi, to_dm_) for meeting_noi, to_dm_ in notify_output_init
            if meeting_noi not in [meeting_nos for meeting_nos, _ in notify_output_soon]
        ]

        # If there are meetings to notify init, print it in the auto channel.
        if notify_output_init:
            print('Sending init notify…')

            for suboutput in chop_output(
                'Reminder that the following meeting(s) are upcoming:\n'
                f'{'\n'.join([
                    f'{(
                        meeting_data[0].to_discord(
                            index = meeting_data[1],
                            pings_to_names = pings_to_names
                        )
                    )}\n{' '.join(meeting_data[0].get_participants())}'
                    for meeting_data in notify_output_init
                ])}'
            ): await notify_channel.send(suboutput)

            print('Init notified!')
        else: print('No init to notify.')

        # If there are pings to dm, dm them.
        # Only do so for initial notification.
        if to_dm:
            failed_dms_output = await dm_notifications(
                bot = bot,
                pings_to_names = pings_to_names,
                to_dm = to_dm
            )
            print('DMs have been sent!')

            if failed_dms_output: await notify_channel.send(failed_dms_output)

        print(DIVIDER_STR)

        # Sleep for the specified interval.
        await sleep(CHECK_INTERVAL_SECS)


# DRIVER BLOCK
if __name__ == '__main__':
    print(f'Current working directory: {getcwd()}')

    load_local_dotenv(__file__)

    bot_token = getenv(GETENV_BOT_TOKEN)
    print(f'Bot token: {repr(bot_token)}')

    bot.run(bot_token)
