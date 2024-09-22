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


## PyQt5 School Management System Overview
This project is a Python-based application that uses PyQt5 to build a graphical user interface (GUI) for managing students, instructors, and courses in a school system. The project integrates SQLite as the database backend and follows an MVC-like architecture to separate logic, database management, and user interface components. The project also includes detailed documentation using Sphinx.

## Project Structure
- `classes.py`: Contains the object-oriented class definitions for Person, Student, Instructor, and Course, as well as input validation functions.
- `databases.py`: Manages the database setup, CRUD operations, and connections for students, instructors, courses, enrollments, and assignments.
- `pyqt_main.py`: The main file to launch the PyQt5-based GUI application. Handles the creation and management of the Student, Instructor, and Course tabs within the PyQt5 interface.
- `sphinx-docs`: Contains Sphinx configuration for auto-generating documentation from the project.
- `requirements.txt`: Lists all the dependencies required to run the project.

## Requirements
Before running the project, install the required dependencies using the requirements.txt file. Run the following command to install them:

```bash
pip install -r requirements.txt
```


## How to Run the Project
- Ensure that Python is installed on your system.
- Clone the repository into a folder of your choice:
```bash
git clone <project-link>
```
- Install the dependencies listed in requirements.txt:
```bash
pip install -r requirements.txt
```
-To run the PyQt5-based School Management System, execute:
```bash
python pyqt_main.py
```
This will launch the application, providing you with an interface to manage students, instructors, and courses.

## Additional Information
- `Student Management`: Add, update, delete, and search for students. Each student can be assigned to a course, and their information can be exported to a CSV file.
- `Instructor Management`: Add, update, delete, and search for instructors. Instructors can be assigned to teach specific courses.
- `Course Management`: Add, update, delete, and search for courses. Courses display assigned instructors and enrolled students.
- `Backup and Restore`: The project includes backup and restore functionality for the SQLite database.
The database is created automatically if it does not exist when running the application. The GUI is built using PyQt5 with a tab-based interface, allowing easy navigation between managing students, instructors, and courses.



