'''Frodo Meet - Show Meetings Command
'''
from discord import Interaction

from common.common_bot_helper import parse_input

from frodo_meet_helper import get_meetings_to_discord

from meeting import Meeting


async def show_meetings(
    interaction: Interaction,
    meetings: list[Meeting],
    ids_to_names: dict[str: str],
    filters: str
) -> None:
    print('Show meetings command start.')

    await interaction.response.send_message(get_meetings_to_discord(
        meetings,
        ids_to_names,
        parse_input(filters, ' ')
    ))

    print('Show meetings command end.')
