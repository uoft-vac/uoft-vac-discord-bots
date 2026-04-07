'''Frodo Meet
Author: Sunny Lin
Editors: 
Last modified: Jul 6, 25

Uoft (St. George campus) Visual Arts Club exec team's Discord bot for easy meeting plan management.

Can add, cancel, & edit meeting plans with Discord commands.
Also notifies meeting members when a meeting is about to start.
Stores and reads meeting data in meeting_entries.json.

Frameworks & drivers file.

Not for public use.
'''
# TODO: add, cancel, edit functions.
# TODO: Check + notify auto function.

from discord import Intents
from discord.ext import commands

from asyncio import sleep
from time import time, strftime

import common_bot_helper
import frodo_meet_commands

# CONSTANTS:

CHANNEL_ID = ... # TODO: Channel ID for the meeting notification channel.
ENTRIES_FILE_PATH = 'meeting_entries.json'

WORD_LIMIT = 2000 # Word limit for Discord messages; might vary, but this is a safe value.
CHECK_INTERVAL = 60 # Seconds between each check for upcoming meetings.


client = commands.Bot(command_prefix = '.', intents = Intents.all())

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    client.loop.create_task(check_and_notify())


# COMMAND FUNCTIONS:

@client.command(pass_context = True)
async def show(ctx, *args) -> None:
    await ctx.send(frodo_meet_commands.show(
        args,
        common_bot_helper.read_json_file(ENTRIES_FILE_PATH),
        time(),
    ))

@client.command(pass_context = True)
async def add(ctx, *args) -> None:
    await ctx.send(frodo_meet_commands.add(
        args,
        common_bot_helper.read_json_file(ENTRIES_FILE_PATH),
    ))

@client.command(pass_context = True)
async def cancel(ctx, *args) -> None:
    await ctx.send(frodo_meet_commands.cancel(
        args,
        common_bot_helper.read_json_file(ENTRIES_FILE_PATH),
    ))

@client.command(pass_context = True)
async def edit(ctx, *args) -> None:
    await ctx.send(frodo_meet_commands.edit(
        args,
        common_bot_helper.read_json_file(ENTRIES_FILE_PATH),
    ))


# AUTO FUNCTIONS:

async def check_and_notify() -> None:
    await client.wait_until_ready()
    while not client.is_closed():
        ...


# THE CODE BODY BELOW CONTAINS SENSITIVE INFORMATION; KEEP COMPRESSED.
if __name__ == '__main__':
    client.run('MTM5MTIwNDQ3MjQwNzA2NDY4OA.GsICWF.64EdmwlT3BDEqV11ZZYaDuz03oyt548Ild3crQ')
