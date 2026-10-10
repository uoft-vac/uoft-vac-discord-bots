'''Common - File

Functions to help with read from/writing to files.
'''
from json import load, dump


def read_json_file(file_path: str) -> dict:
    with open(file_path, 'r') as f: return load((f))

def write_json_file(file_path: str, data: dict, indent: int = 4) -> None:
    with open(file_path, 'w') as f: dump(data, f, indent = indent)


if __name__ == '__main__':
    from doctest import testmod
    testmod()
