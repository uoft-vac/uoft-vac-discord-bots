'''Frodo Meet - Show Meetings Command
'''
from discord import Interaction

from common.util import parse_input

from frodo_meet_helper import get_meetings_to_discord
from meeting import Meeting


async def show_meetings(
    interaction: Interaction,
    meetings: list[Meeting],
    filters: str
) -> None:
    print('Show meetings command start.')

    await interaction.response.send_message(get_meetings_to_discord(
        interaction, meetings, parse_input(filters, ' ')
    ))

    print('Show meetings command end.')
