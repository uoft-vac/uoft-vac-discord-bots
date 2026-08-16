# Here are the UofT Visual Arts Club's Discord bots.

Operations are subject to change based on future webmasters' discretions.

---
### <mark><u>IMPORTANT</u></mark>

Never reveal <mark><u>**PRIVATE BOT TOKENS**</u></mark> to the public.
\
Since the repo is public, this means not pushing any files containing this data to GitHub.
\
Instead, keep this data in **environment files** only, which should be in [`.gitignore`](.gitignore).

Unauthorised access to tokens could allow someone to **take control of the bots**, thereby causing damage to them and/or the Discord server(s).
\
If you know or even suspect someone has unauthorised access to this data, <u>**regenerate the bot's token immediately**</u>.

---
### Implementation

Currently, the bots are programmed in **Python** using the **Python Discord API**.

I've also included a a rough [template](bot_template.py) file that I wrote for starting to program new Discord bots in case the club ever wants more.

---
### Organisation

Refer to [Frodo Meet](frodo-meet) as an example bot directory.

All bots should have their **own directory** under this repo, and all files specific to a bot should be kept in their directory. \
Furthermore, all files required for hosting should be in a `bot` subdirectory (other than files in [`common`](common)).

A bot will likely have these components for hosting:
- **Driver file**: Single file that uses Discord API to communicate with Discord directly and uses functions from helper files to execute tasks & get outputs ([e.g.](frodo-meet/bot/frodo_meet.py)).
- **Computation layer**: files containing functions, classes, variables, views, etc, for executing tasks and computing output. ([e.g.](frodo-meet/bot/frodo_meet_helper.py)).
- [`requirements.txt`](frodo-meet/bot/requirements.txt): lists the bot's dependencies.
    - Each bot will have separate dependencies and will be installed in their own venvs.
- **Data layer**: Data files, if data needs to persist.
    - These files should **not** be pushed to GitHub as they may be modified during testing on local machines, and pulling these files onto the hosting service may override existing data.
    - Include these particular files in `.gitignore`.
    - Create new copies of these files on the hosting service.

When editing a bot or starting a new one, try to be consistent with its and other bots' organisation, unless the bot's functionality requires otherwise.

---
### Hosting

The bots will be hosted on a **Raspberry Pi** situated in the **club office**.
\
For details on how to operate the Pi, read the [Pi Manual](pi-manual.md).
