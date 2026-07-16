'''Frodo Meet

UofT Visual Arts Club exec team's Discord bot for easy meeting plan management.

Can create and manage meeting with Discord commands.
Also notifies meeting members when a meeting is about to start.
Stores and reads meeting data in meetings_data.json.

Driver file.
'''
greet_on_boot = True # Toggleable

from discord import Intents, Interaction, TextChannel
from discord.ext import commands

from asyncio import sleep
from os import getcwd, getenv

from common.util import (
    load_local_dotenv,
    chop_output,
    get_ids_to_names,
    GETENV_BOT_TOKEN,
    DIVIDER_STR,
)

from frodo_meet_data import load_meetings, get_meetings, save_meetings
from meeting_time import MeetingTime
import command_show, command_create, command_delete, command_edit, command_toggle_active
from frodo_meet_background_tasks import notify_meetings, begin_meetings, dm_notifications


# CONSTANTS

CHECK_INTERVAL_SECS = 60 # Seconds between each check for meetings to notify/begin.
NOTICE_TIME_SECS = 5 * 60 # Notify meetings that will begin in less than this number of minutes.


# SETUP

intents = Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='.', intents=intents)
tree = bot.tree
command = tree.command

background_task = None

@bot.event
async def on_ready():
    global background_task

    load_meetings()

    await tree.sync()
    print(f'Logged in as {bot.user}.')

    notify_channel = bot.get_channel(int(getenv('NOTIFY_CHANNEL_ID')))
    if greet_on_boot: await notify_channel.send('Frodomeet clocking in! 🫡')

    if background_task is not None:
        print('Background task already exists. 🧐')
        return

    print('Beginning background task.')
    background_task = bot.loop.create_task(auto_notify_n_begin(
        notify_channel, NOTICE_TIME_SECS
    ))


# COMMANDS

@command(
    name = 'show-meetings',
    description = 'Display recorded meeting plans.'
)
async def show_meetings(interaction: Interaction, filters: str = '') -> None:
    print(
        f'{DIVIDER_STR}\n'
        f'Show meetings command prompted, calling command.'
    )
    await command_show.show_meetings(
        interaction,
        get_meetings(),
        get_ids_to_names(interaction.guild),
        filters
    )

@command(
    name = 'create-meeting',
    description = 'Create a new meeting!'
)
async def create_meeting(interaction: Interaction) -> None:
    print(
        f'{DIVIDER_STR}\n'
        f'Create meeting command prompted, calling command.'
    )
    await command_create.create_meeting(
        interaction,
        get_meetings(),
        get_ids_to_names(interaction.guild)
    )

@command(
    name = 'delete-meeting',
    description = 'Delete an existing meeting!'
)
async def delete_meeting(interaction: Interaction, target: str = None) -> None:
    print(
        f'{DIVIDER_STR}\n'
        f'Delete meeting command prompted, calling command.'
    )
    await command_delete.delete_meeting(
        interaction,
        get_meetings(),
        get_ids_to_names(interaction.guild),
        target
    )

@command(
    name = 'edit-meeting',
    description = 'Edit a property for an existing meeting!'
)
async def edit_meeting(interaction: Interaction, target: str = None) -> None:
    print(
        f'{DIVIDER_STR}\n'
        f'Edit meeting command prompted, calling command.'
    )
    await command_edit.edit_meeting(
        interaction,
        get_meetings(),
        get_ids_to_names(interaction.guild),
        target
    )

@command(
    name = 'toggle-active',
    description = 'Activate an inactive meeting, or deactivate an active meeting!'
)
async def toggle_active(interaction: Interaction, target: str = None) -> None:
    print(
        f'{DIVIDER_STR}\n'
        f'Toggle active command prompted, calling command.'
    )
    await command_toggle_active.toggle_active(
        interaction,
        get_meetings(),
        get_ids_to_names(interaction.guild),
        target
    )

@command(
    name = 'help-frodo-meet',
    description = 'Need help with my functions? I got you!'
)
async def hi_frodo_meet(interaction: Interaction) -> None:
    print(
        f'{DIVIDER_STR}\n'
        f'Help command prompted, calling command.'
    )
    ...

@command(
    name = 'hi-frodo-meet',
)
async def hi_frodo_meet(interaction: Interaction) -> None:
    print(
        f'{DIVIDER_STR}\n'
        f'Hi command prompted, calling command.'
    )
    ...


# BACKGROUND TASKS

async def auto_notify_n_begin(notify_channel: TextChannel, notice_time_secs: int) -> None:
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

        # Check for any meetings to notify and get the output.
        notify_output, to_dm = notify_meetings(meetings, now, notice_time_secs)
        print('Got notify result.')

        # Check for any meetings to begin and get the output.
        begin_output = begin_meetings(meetings, now)
        print('Got begin results.')

        # If meetings are modified, save data.
        if notify_output or begin_output: save_meetings()

        # If there are meetings to notify, print it in the auto channel.
        if notify_output:
            for suboutput in chop_output(notify_output):
                await notify_channel.send(suboutput)
            print('Meetings have been notified!')
        else: print('No meetings to notify.')

        # If there are pings to dm, dm them.
        if to_dm:
            failed_dms_output = await dm_notifications(
                bot, to_dm,
                get_ids_to_names(bot.get_guild(int(getenv('SERVER_ID'))))
            )
            print('DMs have been sent!')

            if failed_dms_output: await notify_channel.send(failed_dms_output)

        # If there are meetings that have begun, print it in the auto channel.
        if begin_output:
            for suboutput in chop_output(begin_output):
                await notify_channel.send(suboutput)
            print('Meetings have begun!')
        else: print('No meetings to begin.')

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
