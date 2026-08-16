'''Frodo Meet - Help Command
'''
from discord import Interaction

from os import getenv

from frodo_meet_data import GETENV_NOTIFY_CHANNEL_ID

SUBOUTPUTS = (
'''
# Meetings

A meeting has the following properties:
- Title (required)
- Time (required)
- Description
- Participants
- Ping by dm
- Recurrence
- Active status
## Title Input Specifications

Title must be **unique** among the meetings in the meeting list.
## Time Input Specifications

**Formats:**
**(5)** Year Month Day Hour Minute
**(4)** Month Day Hour Minute
**(3a)** Year Month Day
**(3b)** Weekday Hour Minute
**(2a)** Month Day
**(2b)** Hour Minute
**(1)** Weekday

- A time in invalid if it is __already passed__.
- For month and weekday, you can enter its number, full name, or abreviation.
> e.g. `12`, `december`, and `dec` all work.
> Note: Use `tues` and `thurs` for their abreviations; all others are the first 3 characters.
- If the hour and minute are not specified, it'll default to __6:00pm__.
- If no year is specified, it'll result in the **next instance** of that time.
> e.g. if it is currently __August 14 of 2026__ and you enter `8 15 0 0` for **(4)**, it'll result in the __next day__.
> But if you enter `8 13 0 0` for **(4)**, it'll result in __August 13 of 2027__.

**Note:**
There are two formats with 3 arguments and 2 arguments.
The bot will prioritise the **a** format, and will only use the **b** format if the first format is invalid given the data.
e.g.
- Entering `12 31` will result in December 31, not the next instance of 12:31pm.
- Entering `13 31` will result in the next instance of 1:31pm since there is no 13th month.

This also means if you want to have for example 12:13pm, you'll need to use a more explicit input, like `2 12 31` for Monday 12:31pm, assuming you're doing this before the intended time.
> It does not use the **3a** format because year 2 is long passed.
''', #
f'''
## Participants/Ping by DM Input Specifications

Enter the **display names** for all participants you want to add for this meeting, separated by commas. Can have roles and users __with the **Exec** role__. Not case or outerspace-sensitive.
- e.g. `sunny, lead, sy, admin, frodo meet, secretary`
- Note that it's display names, __not usernames__ (use `sunny`, not `deltahedra`).
- __Not outerspace-sensitive__: whitespace on the edges of each argument will be ignored (e.g. `   sunny   ` and `sunny` will be the same, but `frodo meet` and `frodo   meet` are different).

**Note:** It'll only consider users with the **Exec** role.
- This is because users in the server could have the same display name. This'll allow the bot to only consider the relevant users, reducing the chance of name conflicts.
- If two current execs have the same name, they must find a way to resolve it (e.g. naming with their last initials.)

Participants and ping by dm have the exact type of input structure.
## Recurrence

**Options:** normal (one-time), daily, weekly, and yearly.

When a normal meeting starts, it is deleted.
When a recurring meeting starts, a clone of it will be created at the appropriate time.
## Active Status

Active meetings will produce notification messages when it'll start soon and start messages when it starts in <#{getenv(GETENV_NOTIFY_CHANNEL_ID)}>.
Inactive meetings won't produce any message, but will still be deleted/cloned when applicable.

Use **/toggle-active** to edit the active status of meetings.

If you encounter any issues or are still confused, **feel free to ask Sunny!**
'''
)


async def help(
    interaction: Interaction
) -> None:
    print('Help command start.')

    await interaction.response.send_message(SUBOUTPUTS[0])
    for suboutput in SUBOUTPUTS[1:]:
        await interaction.channel.send(suboutput)

    print('Help command end.')
