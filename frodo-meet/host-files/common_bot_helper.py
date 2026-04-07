'''Common Bot Helper
Author: Sunny Lin
Editors: 
Last modified: Jul 6, 25

Contains functions that many bots will likely find useful.
To be deployed along with bot host files.
'''
import json


# File functions:
def read_json_file(file_path: str) -> dict:
    with open(file_path, 'r') as f: return json.load((f))

def write_json_file(file_path: str, data: dict) -> None:
    with open(file_path, 'w') as f: json.dump(data, f, indent = 4)


# Input functions:
def parse_input(input: str, breakpoint: str) -> list[str]:
    '''
    Given an input string and breakpoint string,
    return a list of the arguments (substrings) from the input
    divided by the breakpoint.
    Also make all arguments lowercase.

    Sample Usage:
    >>> parse_input('hello hi', ' ')
    ['hello', 'hi']

    >>> parse_input(' Hello  HI   ', ' ')
    ['hello', 'hi']

    >>> parse_input('hello hi, greetings', ',')
    ['hello hi', 'greetings']

    >>> parse_input('hello hi', 'hello')
    ['hi']
    '''
    return [arg.strip().lower() for arg in input.split(breakpoint) if arg.strip()]


# Discord functions:
def chop_output(output: str, limit: int) -> tuple[str]:
    '''
    Given a string to be outputted, return a tuple containing chopped parts of the output,
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
    # Split the output at all line breaks.
    lines = output.split('\n')

    # Construct the output list.
    chopped = []
    start = 0
    end = 1

    # Go until the end of the list.
    while end != len(lines) + 1:

        # Get the current substring.
        substring = '\n'.join(lines[start: end])

        # If the length of the substring exceeds the minimum and it contains at least one line break,
        # append the previous substring to the output list and start from the start of the current substring.
        if len(substring) > limit and start != end - 1:
            chopped.append('\n'.join(lines[start: end - 1]))
            start = end - 1

        # Otherwise, the next line will be considered.
        else:

            # If the length of the substring is equal to the minimum,
            # append the current substring to the output list and start from the end of the current substring.
            if len(substring) == limit:
                chopped.append(substring)
                start = end

            # Extend to the next line.
            end += 1

    # If the start index does not immediately precede the end index,
    # then the last lines have not been added, so add them and return the output list.
    if start != end - 1:
        return chopped + ['\n'.join(lines[start:])]

    # Otherwise, all lines have been added, so return the output list.
    return chopped


if __name__ == '__main__':
    from doctest import testmod
    testmod()
