'''Common - Discord ID

Functions to manipulate Discord IDs for various tasks.
'''
from discord import User, Guild
from discord.ext.commands import Bot

from re import search


def get_pings_to_names(guild: Guild) -> dict[str: str]:
    '''Return a dictionary of ping-name pairs for the guild's roles and members.'''
    roles_dict = {f'<@&{role.id}>': role.name for role in guild.roles}
    members_dict = {f'<@{member.id}>': member.display_name for member in guild.members}
    # print(roles_dict, members_dict)

    return roles_dict | members_dict


async def get_users_from_ping(
    bot: Bot,
    ping: str,
) -> list[User]:
    '''
    If given a role ping, return a list of all members of that role as users.
    If given a user ping, return a list containing that user.

    If not found, return None.
    '''
    users: list[User] = []

    id = int(search(r'\d+', ping).group())

    if '&' in ping:
        for guild in bot.guilds:
            role = guild.get_role(id)
            if role:
                users = role.members
                break
    
    else:
        user = bot.get_user(id)
        if not user: user = await bot.fetch_user(id)
        users = [user]
    
    return users


if __name__ == '__main__':
    from doctest import testmod
    testmod()
