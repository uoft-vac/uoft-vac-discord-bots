'''Common - Input

Functions to help read, process, facilitate Discord user inputs.
'''
from discord import Interaction, Message, ButtonStyle
from discord.ui import View, button, Button

from re import split

# Bots will stop waiting for responses after this number of seconds.
RESPONSE_TIMEOUT = 60
# Discord select values must be nonempty strings, so use this for null option (unless it is used for a legitemate option).
NULL_SELECT_VALUE = '0'
# Max number of select options for one message (supposedly).
MAX_SELECTS = 25


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

    def __init__(self,
        on_confirm: callable,
        on_cancel: callable,
        **data: dict
    ):
        print('In confirmation view, awaiting confirmation…')
        super().__init__(timeout = RESPONSE_TIMEOUT)

        self._on_confirm = on_confirm
        self._on_cancel = on_cancel
        self._data = data
    
    @button(label = 'Yes', style = ButtonStyle.green)
    async def confirm(self, interaction: Interaction, _: Button):
        print('Confirmed, executing on confirm process.')
        await self._on_confirm(interaction, **self._data)
    
    @button(label = 'No', style = ButtonStyle.red)
    async def cancel(self, interaction: Interaction, _: Button):
        print('Cancelled, executing on cancel process.')
        await self._on_cancel(interaction, **self._data)


def parse_input(
    input: str,
    breakpoints_re: str,
    strip_points: str = ' ',
    lower: bool = True
) -> list[str]:
    '''
    Given an input string and a regex of breakpoints,
    return a list of the args (substrings) from the input split by the breakpoints.
    Can choose to strip and/or make args lowercase.
    '''
    result = [arg for arg in split(breakpoints_re, input) if arg]
    if strip_points: result = [arg.strip(strip_points) for arg in result]
    if lower: result = [arg.lower() for arg in result]
    return result


if __name__ == '__main__':
    from doctest import testmod
    testmod()
