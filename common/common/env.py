'''Common - Environment

Functions to interact with environment variables.
'''
from dotenv import load_dotenv
from pathlib import Path

# Common string used to get the bot's token from the environment (each bot should have their own environment).
GETENV_BOT_TOKEN = 'BOT_TOKEN'


def load_local_dotenv(file: str) -> None:
    '''Call dotenv.load_dotenv on the .env at the same level as the driver file.'''
    load_dotenv(Path(file).parent / '.env')


if __name__ == '__main__':
    from doctest import testmod
    testmod()
