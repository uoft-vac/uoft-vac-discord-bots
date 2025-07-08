'''Discord Bot Template
Author(s): Sunny Lin
Editor(s): N/A
Last edited: Jul 5, 25

This is a template file for starting to program Discord bots in Python.
It should have most features a basic bot could need like command functions and auto functions.
This file is not meant to be run.

TODO: Fill out information above according to your bot's purposes.
'''

from discord import Intents
from discord.ext import commands
...

# Constants:
...


# TODO: Set command_prefix (str) to the command prefix of choice.
# A command prefix is the symbol at the beginning of every bot command message.
# E.g. Use '.' for commands like ".show", or use '/' for commands like "/help".
# '.' is the easiest in my opinion.
client = commands.Bot(command_prefix = ..., intents = Intents.all())

# When the bot goes online.
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

    # Connect all auto functions.
    client.loop.create_task(auto_func_eg)


# Command functions: functions that fire when a Discord user types in the command name.
# The function name is the command name.
# E.g. If the function name is command_func_eg, then the user would type ".command_func_eg …"
@client.command(pass_context = True)
async def command_func_eg(ctx) -> None:
    ...

...


# Auto functions: functions that fire when the bot goes online.
async def auto_func_eg() -> None:

    # Begin only when the bot is online.
    await client.wait_until_ready()

    # Program loop; keep running unless the bot goes offline.
    while not client.is_closed():
        ...


# Activate bot.
if __name__ == '__main__':

    # TODO: Enter the bot's private token (str) into the parameter of client.run.
    # DO NOT REVEAL A BOT'S TOKEN TO ANYONE OUTSIDE THE DEV TEAM.
    # If someone has access to a bot's token, they will be able to fully control it and cause damage to the bot and servers.
    # If you know someone outside the dev team has access to the token (or even suspect it), regenerate a new token immediately.
    client.run('')
