'''Frodo Meet
Author: Sunny Lin
Editors: 
Last modified: Apr 7, 26

UofT Visual Arts Club exec team's Discord bot for easy meeting plan management.

Can create and manage meeting with Discord commands.
Also notifies meeting members when a meeting is about to start.
Stores and reads meeting data in meeting_entries.json.

Driver file.
'''
# TODO: Cancel, edit functions.
# TODO: Check + notify auto function.

from discord import Intents, Interaction
from discord.ext import commands

from asyncio import sleep

from common_bot_helper import read_json_file, chop_output

import frodo_meet_commands
from frodo_meet_data import get_meetings, write_meetings, DATA_FILE_PATH
from meeting_time import MeetingTime

from add_input_modal import AddInputModal


# CONSTANTS

NOTIFY_CHANNEL_ID = 1491494362205392976

CHECK_INTERVAL_MINS = 1 # Minutes between each check for upcoming meetings.
NOTICE_TIME_MINS = 5 # Notify meetings that will begin in less than this number of minutes.
WORD_LIMIT = 2000 # Word limit for Discord messages; might vary, but this is a safe value.


intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print('Logged in as {0.user}'.format(bot))
    bot.loop.create_task(auto_notify())


# COMMAND FUNCTIONS

@bot.command(pass_context = True)
async def show(ctx, *args) -> None:
    await ctx.send(frodo_meet_commands.show(
        args,
        get_meetings(read_json_file(DATA_FILE_PATH))
    ))

@bot.tree.command(name='add', description='Create a new meeting!')
async def add(interaction: Interaction) -> None:
    await interaction.response.send_modal(AddInputModal(
        get_meetings(read_json_file(DATA_FILE_PATH))
    ))


# AUTO FUNCTIONS

async def auto_notify() -> None:
    '''
    Every specified interval, check if there are any meetings that are about to start.
    If there are, print a notify message in the notify channel.

    Sample Usage inapplicable.
    '''
    # Proceed when bot is online.
    await bot.wait_until_ready()

    notify_channel = bot.get_channel(NOTIFY_CHANNEL_ID)
    check_interval_secs = CHECK_INTERVAL_MINS * 60
    notice_time_secs = NOTICE_TIME_MINS * 60

    await notify_channel.send('This is Frodo Meet clocking in! 🫡')
    
    while not bot.is_closed():
        # await notify_channel.send(f'Test: the current time is {MeetingTime.get_now().to_discord()}.')

        meetings = get_meetings(read_json_file(DATA_FILE_PATH))

        # Check for any meetings to notify and get the output.
        output = frodo_meet_commands.notify(
            meetings,
            MeetingTime.get_now(),
            notice_time_secs
        )

        # Update data file.
        write_meetings(DATA_FILE_PATH, meetings)

        # If there are meetings to notify, print it in the notify channel.
        if output:
            for substring in chop_output(output, WORD_LIMIT):
                await notify_channel.send(substring)
            print('Meetings have been notified.')
        
        else: print('No meetings to notify.')

        # Check every specified interval.
        await sleep(check_interval_secs)


# THE CODE BODY BELOW CONTAINS SENSITIVE INFORMATION; KEEP COMPRESSED.
if __name__ == '__main__':
    from os import getcwd
    print(f'Current working directory: {getcwd()}')

    bot.run('MTM5MTIwNDQ3MjQwNzA2NDY4OA.GsICWF.64EdmwlT3BDEqV11ZZYaDuz03oyt548Ild3crQ')
