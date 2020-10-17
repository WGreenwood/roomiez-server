from base64 import b64encode
from os import urandom
from os.path import isfile

import click
import re


def _get_env_file():
    files = [
        ('instance/config.py', 'Using the existing environment'),
        ('default.config.py', 'Using the default environment'),
    ]
    for (filePath, msg) in files:
        if isfile(filePath):
            click.echo(msg)
            return (True, filePath)
    return (False, None)


def _get_file_lines(filePath):
    with open(filePath, 'rb') as f:
        return f.read().decode('utf8').splitlines()


def _generate_secret_key():
    rnd = urandom(64)
    b64 = b64encode(rnd)
    b64 = b64.decode('utf-8')
    return "SECRET_KEY = '{}'\n".format(b64)


@click.command('new-secret', help='Securely generate a new application secret')
@click.option('-f', is_flag=True, default=False,
              help='Force the operation. This will invalidate all existing sessions')
def new_secret(f):
    if not f:
        prompt = click.prompt('This will invalidate all existing sessions. \nWould you like to continue? (y/n)')
        if not prompt or prompt.lower() != 'y':
            click.echo('Aborting...')
            return

    success, filePath = _get_env_file()
    if not success:
        click.echo('Failed to locate a configuration file, are you missing a config.default.py file?')
        return

    lines = _get_file_lines(filePath)
    newLines = []
    secretKeyFound = False
    for line in lines:
        if re.match(r"^SECRET_KEY[ ]*?=[ ]*?['|\"].*['|\"][ ]*?$", line):
            click.echo('Found old secret key, generating a new key')

            newLines.append(_generate_secret_key())
            secretKeyFound = True
        else:
            newLines.append(line + '\n')
    if not secretKeyFound:
        click.echo('No secret key was found, generating a new key')
        newLines.append(_generate_secret_key())

    click.echo('Writing new configuration file')
    with open(filePath, 'w') as file:
        file.writelines(newLines)
