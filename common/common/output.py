'''Common - Output

Functions to help facilitate outputs to Discord.
Sending messages or dming users.
'''
from discord import Interaction, User, Forbidden
from discord.abc import GuildChannel
from discord.ext.commands import Bot

from common.discord_id import get_users_from_ping

# Word limit for Discord messages; might vary, but 2000 is a safe value.
WORD_LIMIT = 2000


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


async def dm_user(user: User, message: str) -> int:
    '''
    DM a user with the given message.
    Return 0 on success, -1 on fail.
    '''
    try:
        await user.send(message)
        return 0
    except Forbidden: return -1


async def restrict_to_channel(interaction: Interaction, channel: GuildChannel) -> bool:
    '''
    Return True if the interaction is in the given channel.
    Otherwise, print a message and return False.
    '''
    if interaction.channel == channel: return True

    await interaction.response.send_message(
        f'Please use {channel.mention}.',
        ephemeral = True
    )
    return False


async def dm_users_from_pings(
    bot: Bot,
    pings: list[str],
    pings_to_names: dict[str: str],
    message: str
) -> list[User]:
    '''
    DM all users from the given pings a given message.
    Return a list of users who were failed to DM, if any.

    Note: the given message is IN ADDITION to the greeting on the first line;
    the greeting is sent automatically in this function.
    '''
    failed_users: list[User] = []
    sent_users: list[User] = []

    for ping in pings:
        users: list[User] = await get_users_from_ping(bot, ping)

        for user in users:
            # If message has already been sent to this user, skip.
            if user in sent_users: continue
            sent_users.append(user)

            # Otherwise, send message.
            if await dm_user(user, (
                f'Hey, {pings_to_names[f'<@{user.id}>']}! 👋\n'
                f'{message}'
            )) == -1:
                failed_users.append(user)
    
    return failed_users


if __name__ == '__main__':
    from doctest import testmod
    testmod()
