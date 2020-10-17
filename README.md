# roomiez_server - Capstone Project 2

## This project is archived and no longer maintained

## Cloning & Setup
* Notes:
    * Use one terminal for all the commands

* **Note for Windows Users**:
    * Visit https://visualstudio.microsoft.com/downloads/
    * Be sure you have `Microsoft Visual C++ Build Tools` installed
---
* Setting up the repository
    * Clone the repository
        * ```git clone  https://github.com/WGreenwood/roomiez-server.git```
        * ```cd roomiez-server```
    * Create the virtual environment
        * ```python3 -m venv env```
    * Activate the virtual environment
        * Windows: ```env\Scripts\activate.bat```
        * Mac: ```source env/bin/activate```
    * Update the virtual environment and install requirements
        * ```pip install --upgrade pip setuptools```
        * ```pip install -r dev-requirements.txt ```
    * Install roomiez_server
        * ```pip install -e .[testing,dev]```
---
* Setting up the database
    * Open [roomiez_server/config/development.py](roomiez_server/config/development.py)
    * Confirm the credentials in the ```SQLALCHEMY_DATABASE_URI``` property are correct
    * Open your favorite database management tool (ex. PHPMyAdmin)
    * Create two new databases named ```roomiez_dev``` and ```roomiez_testing```
    * Run ```flask db upgrade``` in the terminal to initialize the database
---
