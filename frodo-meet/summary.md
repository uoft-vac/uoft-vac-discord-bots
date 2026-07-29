# Frodo Meet
Author: Sunny Lin

---
### Meeting Data
Data for a meeting is represented by a [`Meeting`](host-files/meeting.py) object.
\
Data for all meetings are stored in [meeting_entries.json](host-files/meeting_entries.json).
\
Refer to the [sample](meeting_entries_sample.json) file for what this data might look like.

Each meeting object contains 7 attributes:
1. **Title** (`str`)
    - Titles must be **unique** across meetings in the file.
1. **Time**: time the meeting is set to begin ([`MeetingTime`](host-files/meeting_time.py) object)
    - Contains the **UNIX timestamp** and useful functions.
    - Times of existing meetings must be **in the future** (an existing meeting plan for a time in the past doesn't make sense).
1. **Description** (`str`)
    - Can store any single **formatted** Discord message.
1. **Participants**: list of pings (`list[str]`)
    - **Role** pings are represented by `<@&…>`, where … is the <u>role ID</u>.
    - **Member** pings are represented by `<@…>`, where … is the <u>user ID</u>.
1. **Pings by DM**: list of pings by DM (`list[str]`)
    - Same kind of data as <u>participants</u>.
1. **Recurrence** (`str`)
    - `'daily', 'weekly', 'yearly',` or empty string for normal (one-time).
    - A meeting is considered "recurring" if its recurrence is a nonempty string.
1. **Active**: whether to notify (`bool`)
1. **Soon**: whether the meeting has been observed to begin within the notify time. (`bool`)
    - Not directly accessible by the user; only used to mark a meeting as beginning soon.

\
Meetings are stored in **chronological order based on date**.
\
i.e. The first entry in the file should be the closest upcoming one.
