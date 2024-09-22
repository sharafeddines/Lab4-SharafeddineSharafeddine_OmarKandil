# Tkinter Overview

This project is a Python-based application that involves building graphical user interfaces (GUI) using `Tkinter`. The project also includes database setup and class structures, with all necessary dependencies specified in the `requirements.txt` file.

## Project Structure

- `classes.py`: This file contains the object-oriented class definitions for the project.
- `database_setup.py`: This script sets up the database, handles initialization, and defines the schema and connections.
- `tkinter_main.py`: This is the main file to launch the Tkinter-based GUI application.
- `tkinter_tabs.py`: This script handles the creation and management of tabs within the GUI.
- `requirements.txt`: Lists the Python packages and dependencies required to run the project.

## Requirements

Before running the project, install the required dependencies by using the `requirements.txt` file. Run the following command to install them:

```bash
pip install -r requirements.txt
```
The main dependencies include:
- PyQt5: Provides support for more advanced GUI features.
- Sphinx: Used for documentation generation.
- Other libraries such as certifi, docutils, and Jinja2.

The full list of dependencies can be found in the requirements.txt file.

## How to Run the Project
Ensure Python is installed on your system.
Clone the repository in a folder of your choice
``` bash
git clone <project-link>
```
Install the dependencies listed in ```requirements.txt``` in ```tkinter_files``` folder by running:
```bash
pip install -r requirements.txt
```
To run the application, execute the following command:
```bash
python tkinter_main.py
```
This will start the Tkinter GUI application.

## Additional Information
The project uses Tkinter to create windows and manage graphical user components.
The database setup is handled via database_setup.py and should is executed as needed based on your database configuration. If the database of name ```schoolmanagementsystem.db``` is not found, it will be created in the same directory where the python files are found.
The class structure in classes.py ensures modularity, making it easy to expand or integrate into other projects.




