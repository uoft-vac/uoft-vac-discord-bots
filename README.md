# Here are the UofT Visual Arts Club's Discord bots.
Author: Sunny Lin \
Editrs: \
Last modified: Jul 9, 25

---
### <mark><ins>IMPORTANT</ins></mark>
This repository should be kept <mark><ins>**PRIVATE**</ins></mark>.

Certain files contain <ins>sensitive data</ins> (private bot tokens). \
Unauthorised access to this data could allow someone to **take control of the bots**, thereby causing damage to them and/or the Discord server(s).

---
### Implementation
Currently, the bots are programmed in **Python** using the **Python Discord API**.

I've also included a a rough [template](bot_template.py) file that I wrote for starting to program new Discord bots in case the club ever wants more.

---
### Organisation

Refer to [Frodo Meet](frodo_meet) as an example bot folder.

All bots should have their <ins>own folder</ins> under this repo, and all files specific to a bot should be kept in their folder. \
Furthermore, all files required for hosting should be in a <ins>host-files</ins> subfolder (other than the [common bot helper file](common_bot_helper.py)).

A bot will likely have these components for hosting:
- **Driver file**: Single file that uses Discord API to communicate with Discord directly and uses functions from helper files to execute tasks & get outputs ([example](frodo-meet/host-files/frodo_meet.py)).
- **Application business rules layer**: files containing functions for executing tasks and computing output. Independent of Discord API for easy testing ([example 1](frodo-meet/host-files/frodo_meet_commands.py), [example 2](frodo-meet/host-files/frodo_meet_helper.py)).
- **Data layer**: Data files (if data needs to persist). ([example](frodo-meet/host-files/meeting_entries.json)).

When editing a bot or starting a new one, try to be consistent with its and other bots' organisation, unless the bot's functionality requires otherwise.

---
### Hosting
TBD

---
### Want to make changes?
#### Minor changes
If you want to make minor changes, feel free to do them on the spot.
- This includes small corrections to code, comments, or documentation.

#### Larger changes
If you want to make larger changes to a bot's <ins>backend implementation</ins>, discuss with **fellow webmasters**.
- This includes rewriting functions, algorithms, or even entire files.

If you want to add to/alter a bot's <ins>frontend behaviour</ins>, consult with the **rest of the exec team** as well (or just **admins at least**).

#### Tips
Upon <ins>replacing chunks of code</ins>, **comment** old code and keep it in the file for future reference.
> If commented code gets too crowded, designate a **dedicated section** for deprecated code (e.g. at the bottom of the file). \
If a large enough portion of a file's code has been replaced, **writing a new file** could be more efficient.

Upon <ins>replacing entire files</ins>, move old files into the [**archive**](archive) for future reference.
> - The internal organisation of the archive is up to future webmasters' discretion.
> - I suggest giving deprecated file names **additional description**.
>   - E.g. If `frodo_meet.py` was replaced, name the deprecated file `frodo_meet_old.py` or `frodo_meet_v1.py`.

Moreover, always employ <ins>good code practices</ins>:
1. Write <ins>readable code</ins> (meaningful names, type annotations, organise & distinguish tasks).
2. <ins>Express your ideas</ins> (write code comments, function docstrings & tests, file documentations, meaningful commit messages).
3. <ins>Communicate</ins> with the team (announce when you've made significant changes).
4. Write <mark>TODO</mark> comments for any potential development.
    - **Small tasks** can be written where they should be.
    - **Larger tasks** can be written below the file description.

This will help not only you but also fellow & future webmasters.

---
###
And last but not least, <mark>be critical, be responsible, be respectful, be humble, be open to criticism, and do your best</mark>! \
Let's make VAC **better than it was before**!

Oh, and <ins>have fun</ins> as well ; )

### Cheers!
\- SL