# Here are the UofT Visual Arts Club's Discord bots.

Operations are subject to change based on future webmasters' discretions.

---
### <mark><u>IMPORTANT</u></mark>

Never reveal <mark><u>**PRIVATE BOT TOKENS**</u></mark> to the public.
\
Since the repository is public, this means not pushing any files containing this data to GitHub.
\
Instead, keep this data in **environment files** only, which should be in [.gitignore](.gitignore).

Unauthorised access to tokens could allow someone to **take control of the bots**, thereby causing damage to them and/or the Discord server(s).

---
### Implementation

Currently, the bots are programmed in **Python** using the **Python Discord API**.

I've also included a a rough [template](bot_template.py) file that I wrote for starting to program new Discord bots in case the club ever wants more.

---
### Organisation

Refer to [Frodo Meet](frodo-meet) as an example bot folder.

All bots should have their **own folder** under this repo, and all files specific to a bot should be kept in their folder. \
Furthermore, all files required for hosting should be in a **host-files** subfolder (other than the [common bot helper file](common_bot_helper.py)).

A bot will likely have these components for hosting:
- **Driver file**: Single file that uses Discord API to communicate with Discord directly and uses functions from helper files to execute tasks & get outputs ([e.g.](frodo-meet/host-files/frodo_meet.py)).
- **Computation layer**: files containing functions, classes, variables, views, etc, for executing tasks and computing output. ([e.g.](frodo-meet/host-files/frodo_meet_helper.py)).
- **Data layer**: Data files (if data needs to persist). ([e.g.](frodo-meet/host-files/meeting_entries.json)).

When editing a bot or starting a new one, try to be consistent with its and other bots' organisation, unless the bot's functionality requires otherwise.

---
### Hosting

The bots will be hosted on a **Raspberry Pi**, ideally set in the club office (this has yet to be tested).

<u>SETUP IN PROGRESS.</u>

---
### Tips

#### 1. <mark>Communicate</mark> with the team (very important)

- For **backend** changes, can discuss with <u>fellow webmasters</u>.
-  For **frontend** changes, discuss with the <u>exec team</u> (or just <u>admins at least</u>).
- Announce when you've made significant changes relevant to users.

#### 2. Employ good **version control** practices

- **Branch** for distinct tasks.
- Make **pull requests** with clear comments and seek code reviews before merging.
- Write meaningful **commit messages**.

#### 2. Write **readable code**

- Meaningful names.
- Type annotations.
- Organise and distinguish tasks.

#### 3. Make your code intentions clear

- Write code comments.
- Function and class docstrings.
- Tests.

#### 4. Write **TODO** comments for any <u>potential</u> development.

- Small tasks can be written where they should be.
- Larger tasks can be written below the file description.

\
This will help not only you but also fellow & future webmasters.

---
###
And last but not least, <mark>be critical, be responsible, be respectful, be humble, be open to criticism, and do your best</mark>!
\
Let's make VAC **better than it was before**!

Oh, and <u>have fun</u> as well ; )

Test Edit

### Cheers!
\- SL
