'''Common Bot Helper
Author: Sunny Lin
Editors: 
Last modified: Apr 7, 26

Functions that many bots will likely find useful.
To be deployed along with bot host files.
'''
from json import load, dump
from re import split

RESPONSE_TIMEOUT = 60 # Bots will stop waiting for responses after this number of seconds.


# FILE FUNCTIONS

def read_json_file(file_path: str) -> dict:
    with open(file_path, 'r') as f: return load((f))

def write_json_file(file_path: str, data: dict) -> None:
    with open(file_path, 'w') as f: dump(data, f, indent = 4)


# INPUT FUNCTIONS

def parse_input(input: str, breakpoints_re: str) -> list[str]:
    '''
    Given an input string and a regex of breakpoints, return a list of the args (substrings) from the input split by the breakpoints.
    Also make all args lowercase.

    Sample Usage:
    >>> parse_input('-all soon 1 -2', ' ')
    ['-all', 'soon', '1', '-2']

    >>> parse_input(' -ALL  sOoN   1    -2     ', ' ')
    ['-all', 'soon', '1', '-2']

    >>> parse_input('-all soon, 1 -2', ',')
    ['-all soon', '1 -2']

    >>> parse_input('-all, soon ,1 , -2', '[ ,]')
    ['-all', 'soon', '1', '-2']

    >>> parse_input('-all, soon ,1 , -2', ' ,')
    ['-all, soon', '1', '-2']

    >>> parse_input('2025 Jun-7, 18:00', '[ ,:-]')
    ['2025', 'jun', '7', '18', '00']
    '''
    return [
        arg.strip().lower()
        for arg in split(breakpoints_re, input)
        if arg.strip()
    ]


# DISCORD FUNCTIONS

def chop_output(output: str, limit: int) -> tuple[str]:
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
        if len(substring) > limit and start != end - 1:
            chopped.append('\n'.join(lines[start: end - 1]))
            start = end - 1

        # Otherwise, next line will be considered.
        else:

            # If the length of the substring is equal to the minimum,
            # append the current substring to the output list and start from the end of the current substring.
            if len(substring) == limit:
                chopped.append(substring)
                start = end

            # Extend to next line.
            end += 1

    # If start index does not immediately precede the end index,
    # then the last lines have not been added, so add them and return output list.
    if start != end - 1: return chopped + ['\n'.join(lines[start:])]

    # Otherwise, all lines have been added, so return output list.
    return chopped


if __name__ == '__main__':
    from doctest import testmod
    testmod()
