'''Common Bot Helper

Functions that many bots will likely find useful.
To be deployed along with bot host files.
'''
from discord import Interaction, Message, ButtonStyle
from discord.ui import View, button, Button

from dotenv import load_dotenv
from pathlib import Path

from json import load, dump
from re import split

GETENV_BOT_TOKEN = 'BOT_TOKEN' # Common string used to get the bot's token from the environment (each bot should have their own environment).
RESPONSE_TIMEOUT = 60 # Bots will stop waiting for responses after this number of seconds.
WORD_LIMIT = 2000 # Word limit for Discord messages; might vary, but this is a safe value.
NULL_SELECT_VALUE = '0' # Discord select values must be nonempty strings, so use this for null option (unless it is used for a legitemate option).
MAX_SELECTS = 25 # Max number of select options for one message (supposedly).
DIVIDER_STR = '——————————' # To separate prints of background tasks from those of commands, if you wish.


# MACRO FUNCTIONS

def load_local_dotenv(file: str) -> None:
    '''Call dotenv.load_dotenv on the .env at the same level as the driver file.'''
    load_dotenv(Path(file).parent / '.env')


# FILE FUNCTIONS

def read_json_file(file_path: str) -> dict:
    with open(file_path, 'r') as f: return load((f))

def write_json_file(file_path: str, data: dict) -> None:
    with open(file_path, 'w') as f: dump(data, f, indent = 4)


# INPUT FUNCTIONS

async def get_response(interaction: Interaction, timeout: float = RESPONSE_TIMEOUT) -> Message:
    '''
    Awaits and reads a user's input in an interaction.
    Terminates upon timeout.
    '''
    def check(message: Message) -> bool:
        '''From same user in the same channel.'''
        return (
            message.author == interaction.user and
            message.channel == interaction.channel
        )

    try: return await interaction.client.wait_for(
        'message',
        check = check,
        timeout = timeout
    )

    except TimeoutError: await interaction.followup.send('Response timeout. ⚠️')


class ConfirmationViewDefault(View):
    '''
    Prints a message with Yes and No buttons.
    Functions can be passed to specify the task for either case.
    Terminates upon timeout.
    '''
    _on_confirm: callable
    _on_cancel: callable
    _data: dict

    def __init__(
        self,
        on_confirm: callable,
        on_cancel: callable,
        timeout: float = RESPONSE_TIMEOUT,
        **data: dict
    ):
        print('In confirmation view, awaiting confirmation…')
        super().__init__(timeout = timeout)

        self._on_confirm = on_confirm
        self._on_cancel = on_cancel
        self._data = data
    
    @button(label='Yes', style=ButtonStyle.green)
    async def confirm(self, interaction: Interaction, _: Button):
        print('Confirmed, executing on confirm process.')
        await self._on_confirm(interaction, **self._data)
    
    @button(label='No', style=ButtonStyle.red)
    async def cancel(self, interaction: Interaction, _: Button):
        print('Cancelled, executing on cancel process.')
        await self._on_cancel(interaction, **self._data)


def parse_input(input: str, breakpoints_re: str, lower: bool = True) -> list[str]:
    '''
    Given an input string and a regex of breakpoints,
    return a list of the args (substrings) from the input split by the breakpoints.
    Can choose whether to make all args lowercase.
    '''
    return [
        arg.lower() if lower else arg
        for arg in split(breakpoints_re, input)
        if arg
    ]


# OUTPUT FUNCTIONS

def chop_output(output: str, word_limit: int = WORD_LIMIT) -> tuple[str]:
    '''
    Given a string to be printed to Discord, return a tuple containing chopped parts of the string,
    where the chops are at line breaks and each substring is under the given word limit.

    This is so string above the word limit can be sent in multiple messages and still be displayed.

    Sample Usage:
    >>> chop_output('e', 5)
    ['e']

    >>> chop_output('eeeee', 5)
    ['eeeee']

    >>> chop_output('eeeee\\ne', 5)
    ['eeeee', 'e']

    >>> chop_output('eeeee\\neeeee', 5)
    ['eeeee', 'eeeee']

    >>> chop_output('e\\ne\\ne', 5)
    ['e\\ne\\ne']

    >>> chop_output('e\\ne\\ne\\ne', 5)
    ['e\\ne\\ne', 'e']

    >>> chop_output('e\\nee\\neee', 5)
    ['e\\nee', 'eee']

    # Does not chop if a substring itself exceeds the limit, but this is an unrealistic scenario.
    >>> chop_output('eeeeee', 5)
    ['eeeeee']
    '''
    # Split output at all line breaks.
    lines = output.split('\n')

    chopped = []
    start, end = 0, 1
    while end != len(lines) + 1:

        # Get current substring.
        substring = '\n'.join(lines[start: end])

        # If the length of the substring exceeds the minimum and it contains at least one line break,
        # append the previous substring to the output list and start from the start of the current substring.
        if len(substring) > word_limit and start != end - 1:
            chopped.append('\n'.join(lines[start: end - 1]))
            start = end - 1

        # Otherwise, next line will be considered.
        else:

            # If the length of the substring is equal to the minimum,
            # append the current substring to the output list and start from the end of the current substring.
            if len(substring) == word_limit:
                chopped.append(substring)
                start = end

            # Extend to next line.
            end += 1

    # If start index does not immediately precede the end index,
    # then the last lines have not been added, so add them and return output list.
    if start != end - 1: return chopped + ['\n'.join(lines[start:])]

    # Otherwise, all lines have been added, so return output list.
    return chopped


if __name__ == '__main__':
    from doctest import testmod
    testmod()
