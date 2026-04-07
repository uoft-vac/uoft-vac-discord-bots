'''Frodo Meet
Author: Sunny Lin
Editors: 
Last modified: Jul 6, 25

Uoft Visual Arts Club exec team's Discord bot for easy meeting plan management.

Can add, cancel, & edit meeting plans with Discord commands.
Also notifies meeting members when a meeting is about to start.
Stores and reads meeting data in meeting_entries.json.

Frameworks & drivers file.

Not for public use.
'''
# TODO: add, cancel, edit functions.
# TODO: Check + notify auto function.

# Get working directory:
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent

from discord import Intents, Interaction
from discord.ext import commands

from asyncio import sleep
from time import time, strftime

from common_bot_helper import \
    read_json_file
import frodo_meet_commands
from frodo_meet_helper import \
    get_meetings
from add_input_modal import AddInputModal


# CONSTANTS:
NOTIFY_CHANNEL_ID = ... # TODO: Channel ID for the meeting notification channel.
ENTRIES_FILE_PATH = BASE_DIR / "meeting_entries.json"

COMMAND_PREFIX = '.' # For single line commands (e.g. show).
MESSAGE_TIMEOUT = 60 # Bot will stop awaiting messages after this number of seconds.
CHECK_INTERVAL = 60 # Seconds between each check for upcoming meetings.
WORD_LIMIT = 2000 # Word limit for Discord messages; might vary, but this is a safe value.


intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print('Logged in as {0.user}'.format(bot))
    # bot.loop.create_task(check_and_notify())


# COMMAND FUNCTIONS:

@bot.command(pass_context = True)
async def show(ctx, *args) -> None:
    await ctx.send(frodo_meet_commands.show(
        args,
        get_meetings(read_json_file(ENTRIES_FILE_PATH)),
        time(),
    ))

@bot.tree.command(name='add', description='Create a new meeting!')
async def add(interaction: Interaction) -> None:
    await interaction.response.send_modal(AddInputModal())

@bot.command(pass_context = True)
async def cancel(ctx, *args) -> None:
    ...

@bot.command(pass_context = True)
async def edit(ctx, *args) -> None:
    ...


# AUTO FUNCTIONS:

async def check_and_notify() -> None:
    await bot.wait_until_ready()
    while not bot.is_closed():
        ...


# THE CODE BODY BELOW CONTAINS SENSITIVE INFORMATION; KEEP COMPRESSED.
if __name__ == '__main__':
    from os import getcwd
    print(f'Current working directory: {getcwd()}')

    bot.run('MTM5MTIwNDQ3MjQwNzA2NDY4OA.GsICWF.64EdmwlT3BDEqV11ZZYaDuz03oyt548Ild3crQ')
