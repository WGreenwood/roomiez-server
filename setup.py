# https://github.com/kennethreitz/setup.py/blob/master/setup.py

import io
import os
from contextlib import suppress

from shutil import copyfile
from setuptools import find_packages, setup
from setuptools.command.install import install
from setuptools.command.develop import develop

NAME = 'roomiez_server'
DESCRIPTION = 'The rest api backend to the Roomiez mobile application'
URL = 'https://github.com/WGreenwood/roomiez-server'
AUTHORS = [
    'Wesley Fawell-Greenwood <Wesley.Fawell-Greenwood@georgebrown.ca>',
    'Veronica Cheren <Veronica.Cheren@georgebrown.ca>',
    'Trixia Principe <Trixia.Principe@georgebrown.ca>',
]
REQUIRES_PYTHON = '>=3.6.0'
VERSION = None

REQUIRED = [
    'flask',
    'watchdog',
    'python-dotenv',
    'simplejson',
    'PyJWT',
    'mysqlclient',
    'flask_sqlalchemy',
    'flask_migrate',
    'python-dateutil',
]

EXTRAS = {
    'dev': ['flake8', 'rope'],
    'testing': ['pytest', 'coverage']
}

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

about = {}
if not VERSION:
    print(os.path.join(here, NAME, '__version__.py'))
    with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


def mycopy():
    with suppress(OSError):
        if not os.path.exists('.env'):
            copyfile('default.env', '.env')
        os.mkdir('./instance')
        copyfile('default.config.py', './instance/config.py')


class PostInstallCommand(install):
    def run(self):
        mycopy()
        install.run(self)


class PostDevelopCommand(develop):
    def run(self):
        mycopy()
        develop.run(self)


setup(
    name=NAME,
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=', '.join(AUTHORS),
    python_requires=REQUIRES_PYTHON,
    zip_safe=False,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    }
)
