# Frodo Meet
Author: Sunny Lin \
Editors: \
Last modified: Apr 6, 26

---
### Meeting Entries
Refer to the [sample](meeting_entries_sample.json) file for an example of what entries would look like.

Data for meeting plans will be stored in a json file ([meeting_entries.json](host_files/meeting_entries.json)) as entries.

Each entry consists of 5 fields:
1. **title** (`str`)
2. **time**: unix timestamp (`float`)
3. **description** (`str`)
    - Can store any single **formatted** Discord message.
4. **participants**: list of pings (`list[str]`)
    - For **members**, use `<u>…` where … is the <u>user ID</u>.
    - For **roles**, use `<r>…`, where … is the <u>role ID</u>.
    - `everyone` and `here` will work but seem redundant for our purposes (for all execs, ping the exec role).
    - The `<u>` and `<r>` are indicators for replacing IDs with names in the driver file (since this uses the Discord API).
5. **labels**: list of labels (`list[str]`)

\
Entries are stored in **chronological order based on date**.
- i.e. The first entry in the file should be the closest upcoming one.
