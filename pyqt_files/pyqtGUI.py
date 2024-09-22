import sys
import csv
import re
import pickle
import shutil
from classes import Person, Student, Instructor, Course, validate_email, validate_numbers

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog, QComboBox, QHeaderView,
    QAction, QStatusBar, QFormLayout
)
from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import QIntValidator, QRegularExpressionValidator, QIcon
from databases import DatabaseManager

class SchoolManagementSystemApp(QMainWindow):
    """
    Main window for the School Management System application.

    This class represents the main window of the application, providing tabs for managing students,
    instructors, and courses. It allows for saving, loading, exporting, and restoring data from a SQLite
    database and provides additional options for data management, such as exporting to CSV and performing backups.

    """
    def __init__(self):
        """
        Initialize the SchoolManagementSystemApp.

        This method sets up the main window of the application, initializes the database manager, 
        and sets up the tabs for managing students, instructors, and courses.
        """
        super().__init__()
        self.setWindowTitle("School Management System")
        self.setGeometry(100, 100, 1000, 700)
        self.db_manager = DatabaseManager()
        self.init()

    def init(self):
        """
        Initialize the user interface.

        This method creates the menu bar and the main tabs (students, instructors, courses).
        Each tab is connected to a corresponding class that manages the specific entity (StudentTab, InstructorTab, CourseTab).
        """
        self.create_menu_bar()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.tabs = QTabWidget()
        self.student_tab = StudentTab(self)
        self.instructor_tab = InstructorTab(self)
        self.course_tab = CourseTab(self)
        self.tabs.addTab(self.student_tab, "Students")
        self.tabs.addTab(self.instructor_tab, "Instructors")
        self.tabs.addTab(self.course_tab, "Courses")
        self.setCentralWidget(self.tabs)

    def create_menu_bar(self):
        """
        Create the menu bar for the application.

        The menu bar contains options for backing up and restoring the database, saving and loading data, 
        exporting all data to CSV, and exiting the application.
        """
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        backup_action = QAction("Backup Database", self)
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)

        restore_action = QAction("Restore Database", self)
        restore_action.triggered.connect(self.restore_database)
        file_menu.addAction(restore_action)

        file_menu.addSeparator()

        save_action = QAction("Save Data", self)
        save_action.triggered.connect(self.save_data)
        file_menu.addAction(save_action)

        load_action = QAction("Load Data", self)
        load_action.triggered.connect(self.load_data)
        file_menu.addAction(load_action)

        file_menu.addSeparator()

        export_all_action = QAction("Export All to CSV", self)
        export_all_action.triggered.connect(self.export_all_to_csv)
        file_menu.addAction(export_all_action)

        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def backup_database(self):
        """
        Backup the SQLite database to a file selected by the user.

        Opens a file dialog to allow the user to choose the backup location. The database is copied to the
        selected location. Displays a message indicating success or failure.
        """
        backup_file_path, _ = QFileDialog.getSaveFileName(self, "Backup Database", "", "SQLite Database Files (*.db)")
        if backup_file_path:
            try:
                self.db_manager.backup_database(backup_file_path)
                self.status_bar.showMessage(f"Database backed up to {backup_file_path}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to backup database: {str(e)}")

    def restore_database(self):
        """
        Restore the SQLite database from a backup file selected by the user.

        Opens a file dialog for the user to select a backup file. The current database is overwritten with
        the selected file. After restoring, the student, instructor, and course tables are updated. Displays
        a message indicating success or failure.
        """
        backup_file_path, _ = QFileDialog.getOpenFileName(self, "Restore Database", "", "SQLite Database Files (*.db)")
        if backup_file_path:
            try:
                confirm = QMessageBox.question(self, "Confirm Restore", "Restoring will overwrite the current database")
                if confirm == QMessageBox.Yes:
                    self.db_manager.close()
                    shutil.copy(backup_file_path, self.db_manager.db_name)
                    self.db_manager = DatabaseManager()
                    self.student_tab.update_table()
                    self.instructor_tab.update_table()
                    self.course_tab.update_table()
                    self.status_bar.showMessage(f"Database restored from {backup_file_path}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to restore database: {str(e)}")

    def save_data(self):
        """
        Save the current data (students, instructors, courses) to a pickle file.

        Opens a file dialog for the user to select a location. The data is serialized and saved using
        the pickle module. Displays a message indicating success or failure.
        """
        filename, _ = QFileDialog.getSaveFileName(self, "Save Data", "", "Pickle Files (*.pkl)")
        if filename:
            try:
                data = self.export_data()
                with open(filename, 'wb') as f:
                    pickle.dump(data, f)
                QMessageBox.information(self, "Success", "Data saved successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save data: {str(e)}")

    def load_data(self):
        """
        Load data from a pickle file and overwrite the current data.

        Opens a file dialog for the user to select a pickle file. The current data is overwritten by
        deserializing the data from the selected file. The tables for students, instructors, and courses are updated.
        Displays a message indicating success or failure.
        """
        filename, _ = QFileDialog.getOpenFileName(self, "Load Data", "", "Pickle Files (*.pkl)")
        if filename:
            try:
                confirm = QMessageBox.question(self, "Confirm Load", "Loading data will overwrite existing data")
                if confirm != QMessageBox.Yes:
                    return
                with open(filename, 'rb') as f:
                    data = pickle.load(f)
                self.import_data(data)
                self.student_tab.update_table()
                self.instructor_tab.update_table()
                self.course_tab.update_table()
                QMessageBox.information(self, "Success", "Data loaded successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")

    def export_all_to_csv(self):
        """
        Export all students, instructors, and courses data to CSV files.

        Opens a file dialog for the user to select a directory. CSV files are generated for students, instructors,
        and courses, including their associated courses or students where applicable. Displays a message indicating
        success or failure.
        """
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Save CSV Files")
        if directory:
            try:
                student_filename = f"{directory}/students.csv"
                students = self.db_manager.get_all_students()
                with open(student_filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Name", "Age", "Email", "Student ID", "Courses"])
                    for student in students:
                        courses = self.db_manager.get_courses_of_student(student['id'])
                        course_names = ', '.join([course['course_name'] for course in courses])
                        writer.writerow([student['name'], student['age'], student['email'], student['student_id'], course_names])

                instructor_filename = f"{directory}/instructors.csv"
                instructors = self.db_manager.get_all_instructors()
                with open(instructor_filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Name", "Age", "Email", "Instructor ID", "Courses"])
                    for instructor in instructors:
                        courses = self.db_manager.get_courses_of_instructor(instructor['id'])
                        course_names = ', '.join([course['course_name'] for course in courses])
                        writer.writerow([instructor['name'], instructor['age'], instructor['email'], instructor['instructor_id'], course_names])

                course_filename = f"{directory}/courses.csv"
                courses = self.db_manager.get_all_courses()
                with open(course_filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Course Name", "Course ID", "Instructor", "Students Enrolled"])
                    for course in courses:
                        instructor = self.db_manager.cursor.execute('''
                            SELECT instructors.name FROM instructors
                            INNER JOIN assignments ON instructors.id = assignments.instructor_id
                            WHERE assignments.course_id = ?
                        ''', (course['id'],)).fetchone()
                        instructor_name = instructor['name'] if instructor else 'None'
                        students = self.db_manager.cursor.execute('''
                            SELECT students.name FROM students
                            INNER JOIN enrollments ON students.id = enrollments.student_id
                            WHERE enrollments.course_id = ?
                        ''', (course['id'],)).fetchall()
                        student_names = ', '.join([student['name'] for student in students])
                        writer.writerow([course['course_name'], course['course_id'], instructor_name, student_names])

                QMessageBox.information(self, "Success", f"Data exported to CSV files in {directory}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")

    def show_about(self):
        QMessageBox.information(self, "About", "School Management System\nVersion 1.0")

    def closeEvent(self, event):
        """
        Handle the window close event.

        This method ensures that the database connection is properly closed when the application window is closed.
        
        :param event: The close event triggered when the user closes the application.
        :type event: QCloseEvent
        """
        self.db_manager.close()
        event.accept()

    def export_data(self):
        """
        Export all data (students, instructors, courses, enrollments, and assignments) from the database.

        This method fetches all the records from the students, instructors, courses, enrollments, and assignments tables 
        and returns them in a dictionary format.

        :return: A dictionary containing the data for students, instructors, courses, enrollments, and assignments.
        :rtype: dict
        """
        students = self.db_manager.get_all_students()
        instructors = self.db_manager.get_all_instructors()
        courses = self.db_manager.get_all_courses()
        enrollments = self.db_manager.cursor.execute('SELECT * FROM enrollments').fetchall()
        assignments = self.db_manager.cursor.execute('SELECT * FROM assignments').fetchall()

        data = {
            'students': [dict(student) for student in students],
            'instructors': [dict(instructor) for instructor in instructors],
            'courses': [dict(course) for course in courses],
            'enrollments': [dict(enrollment) for enrollment in enrollments],
            'assignments': [dict(assignment) for assignment in assignments]
        }
        return data

    def import_data(self, data):
        """
        Import data into the database.

        This method takes in a dictionary containing the exported data (students, instructors, courses, enrollments, and assignments) 
        and inserts it into the corresponding tables in the database. All existing records are deleted before the new data is inserted.

        :param data: The data to import, containing students, instructors, courses, enrollments, and assignments.
        :type data: dict
        :raises Exception: If an error occurs during the import process.
        """
        self.db_manager.connection.execute('BEGIN TRANSACTION')
        try:
            self.db_manager.cursor.execute('DELETE FROM enrollments')
            self.db_manager.cursor.execute('DELETE FROM assignments')
            self.db_manager.cursor.execute('DELETE FROM students')
            self.db_manager.cursor.execute('DELETE FROM instructors')
            self.db_manager.cursor.execute('DELETE FROM courses')

            for course in data['courses']:
                self.db_manager.cursor.execute('''
                    INSERT INTO courses (id, course_name, course_id) VALUES (?, ?, ?)
                ''', (course['id'], course['course_name'], course['course_id']))

            for student in data['students']:
                self.db_manager.cursor.execute('''
                    INSERT INTO students (id, name, age, email, student_id) VALUES (?, ?, ?, ?, ?)
                ''', (student['id'], student['name'], student['age'], student['email'], student['student_id']))

            for instructor in data['instructors']:
                self.db_manager.cursor.execute('''
                    INSERT INTO instructors (id, name, age, email, instructor_id) VALUES (?, ?, ?, ?, ?)
                ''', (instructor['id'], instructor['name'], instructor['age'], instructor['email'], instructor['instructor_id']))

            for enrollment in data['enrollments']:
                self.db_manager.cursor.execute('''
                    INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)
                ''', (enrollment['student_id'], enrollment['course_id']))

            for assignment in data['assignments']:
                self.db_manager.cursor.execute('''
                    INSERT INTO assignments (instructor_id, course_id) VALUES (?, ?)
                ''', (assignment['instructor_id'], assignment['course_id']))

            self.db_manager.connection.commit()
        except Exception as e:
            self.db_manager.connection.rollback()
            raise e

class StudentTab(QWidget):
    """
    A tab in the School Management System for managing students.

    This tab allows users to add, update, delete, and search for students. It also provides the functionality to
    export student data to a CSV file. The student data is displayed in a table view, with each student
    associated with their name, age, email, student ID, and registered courses.

    :param parent_app: The parent application instance that provides access to shared resources such as the database manager.
    :type parent_app: SchoolManagementSystemApp
    """
    def __init__(self, parent_app):
        """
        Initialize the StudentTab.

        This constructor sets up the interface, connects to the database manager, and creates the input fields, buttons,
        and the table for displaying student data.

        :param parent_app: The parent application instance that provides access to shared resources such as the database manager.
        :type parent_app: SchoolManagementSystemApp
        """
        super().__init__()
        self.app = parent_app
        self.db_manager = parent_app.db_manager
        self.init()

    def init(self):
        """
        Initialize the user interface for the StudentTab.

        This method sets up the input fields for student details, the combo box for course registration, the buttons
        for adding, updating, deleting, and exporting students, and the table for displaying student records.
        """
        self.layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.age_input = QLineEdit()
        self.age_input.setValidator(QIntValidator(1, 150))
        self.email_input = QLineEdit()
        email_regex = QRegularExpression(r"[^@]+@[^@]+\.[^@]+")
        email_validator = QRegularExpressionValidator(email_regex)
        self.email_input.setValidator(email_validator)
        self.id_input = QLineEdit()
        self.id_input.setValidator(QIntValidator(1, 999999))

        self.course_combo = QComboBox()
        self.update_course_combo()

        form_layout.addRow(QLabel("Name:"), self.name_input)
        form_layout.addRow(QLabel("Age:"), self.age_input)
        form_layout.addRow(QLabel("Email:"), self.email_input)
        form_layout.addRow(QLabel("Student ID:"), self.id_input)
        form_layout.addRow(QLabel("Register for Course:"), self.course_combo)

        self.layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Student")
        add_button.clicked.connect(self.add_student)
        update_button = QPushButton("Update Student")
        update_button.clicked.connect(self.update_student)
        delete_button = QPushButton("Delete Student")
        delete_button.clicked.connect(self.delete_student)
        export_button = QPushButton("Export to CSV")
        export_button.clicked.connect(self.export_to_csv)

        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(export_button)

        self.layout.addLayout(button_layout)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Name or ID")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_student)
        clear_search_button = QPushButton("Clear Search")
        clear_search_button.clicked.connect(self.update_table)

        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        search_layout.addWidget(clear_search_button)

        self.layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Age", "Email", "Student ID", "Courses"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellClicked.connect(self.on_table_select)

        self.layout.addWidget(self.table)

        self.update_table()

    def update_course_combo(self):
        """
        Update the course combo box with the list of available courses.

        This method retrieves the available courses from the database and updates the combo box
        to allow the user to register the student for a selected course.
        """
        self.course_combo.clear()
        courses = self.db_manager.get_all_courses()
        course_names = [course['course_name'] for course in courses]
        self.course_combo.addItem("")  
        self.course_combo.addItems(course_names)

    def add_student(self):
        """
        Add a new student to the database.

        This method validates the inputs (name, age, email, and student ID), adds the student to the database,
        and optionally registers the student for a selected course. Displays success or error messages.
        """
        name = self.name_input.text()
        age = self.age_input.text()
        email = self.email_input.text()
        student_id = self.id_input.text()
        course_name = self.course_combo.currentText()
        try:
            age = validate_numbers(age)
            validate_email(email)
            student_id = validate_numbers(student_id)

            student_db_id = self.db_manager.add_student(name, age, email, student_id)

            if course_name:
                course = self.db_manager.get_course_by_name(course_name)
                if course:
                    self.db_manager.enroll_student_in_course(student_db_id, course['id'])

            self.app.status_bar.showMessage("Student added successfully.", 5000)
            self.clear_inputs()
            self.update_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_student(self):
        """
        Update the selected student's details in the database.

        This method validates the inputs (name, age, email, and student ID) and updates the student in the database.
        It also registers the student for a selected course if applicable. Displays success or error messages.
        """
        if not hasattr(self, 'selected_student_db_id'):
            QMessageBox.warning(self, "Warning", "No student selected.")
            return
        name = self.name_input.text()
        age = self.age_input.text()
        email = self.email_input.text()
        student_id = self.id_input.text()
        course_name = self.course_combo.currentText()
        try:
            age = validate_numbers(age)
            validate_email(email)
            student_id = validate_numbers(student_id)

            self.db_manager.update_student(self.selected_student_db_id, name, age, email, student_id)

            if course_name:
                course = self.db_manager.get_course_by_name(course_name)
                if course:
                    self.db_manager.enroll_student_in_course(self.selected_student_db_id, course['id'])

            self.app.status_bar.showMessage("Student updated successfully.", 5000)
            self.clear_inputs()
            self.update_table()
            del self.selected_student_db_id
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_student(self):
        """
        Delete the selected student from the database.

        This method prompts the user for confirmation before deleting the selected student. Displays success or error messages.
        """
        if not hasattr(self, 'selected_student_db_id'):
            QMessageBox.warning(self, "Warning", "No student selected.")
            return
        confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this student?")
        if confirm == QMessageBox.Yes:
            try:
                self.db_manager.delete_student(self.selected_student_db_id)
                self.app.status_bar.showMessage("Student deleted successfully.", 5000)
                self.clear_inputs()
                self.update_table()
                del self.selected_student_db_id
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def on_table_select(self, row, column):
        """
        Handle the event when a student is selected from the table.

        This method populates the input fields with the selected student's data, allowing the user to edit or delete
        the student's details.

        :param row: The row number of the selected student in the table.
        :type row: int
        :param column: The column number of the selected cell in the table.
        :type column: int
        """
        item = self.table.item(row, 0)
        self.selected_student_db_id = item.data(Qt.UserRole)
        student = self.db_manager.cursor.execute('SELECT * FROM students WHERE id = ?', (self.selected_student_db_id,)).fetchone()
        self.name_input.setText(student['name'])
        self.age_input.setText(str(student['age']))
        self.email_input.setText(student['email'])
        self.id_input.setText(str(student['student_id']))
        self.course_combo.setCurrentIndex(0)

    def clear_inputs(self):
        """
        Clear all input fields on the form.

        This method resets the name, age, email, student ID input fields, and the course combo box.
        """
        self.name_input.clear()
        self.age_input.clear()
        self.email_input.clear()
        self.id_input.clear()
        self.course_combo.setCurrentIndex(0)

    def update_table(self):
        """
        Update the student table with the latest data from the database.

        This method clears the current table and fetches all students from the database, populating the table with their details.
        """
        self.table.setRowCount(0)
        students = self.db_manager.get_all_students()
        for student in students:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            item = QTableWidgetItem(student['name'])
            item.setData(Qt.UserRole, student['id'])
            self.table.setItem(row_position, 0, item)
            self.table.setItem(row_position, 1, QTableWidgetItem(str(student['age'])))
            self.table.setItem(row_position, 2, QTableWidgetItem(student['email']))
            self.table.setItem(row_position, 3, QTableWidgetItem(str(student['student_id'])))
            courses = self.db_manager.get_courses_of_student(student['id'])
            course_names = ', '.join([course['course_name'] for course in courses])
            self.table.setItem(row_position, 4, QTableWidgetItem(course_names))
        self.update_course_combo()

    def search_student(self):
        """
        Search for students by name or student ID.

        This method fetches the students matching the search query and updates the table with the results.
        """
        query_text = self.search_input.text().lower()
        self.table.setRowCount(0)
        students = self.db_manager.search_students(query_text)
        for student in students:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            item = QTableWidgetItem(student['name'])
            item.setData(Qt.UserRole, student['id'])
            self.table.setItem(row_position, 0, item)
            self.table.setItem(row_position, 1, QTableWidgetItem(str(student['age'])))
            self.table.setItem(row_position, 2, QTableWidgetItem(student['email']))
            self.table.setItem(row_position, 3, QTableWidgetItem(str(student['student_id'])))
            courses = self.db_manager.get_courses_of_student(student['id'])
            course_names = ', '.join([course['course_name'] for course in courses])
            self.table.setItem(row_position, 4, QTableWidgetItem(course_names))

    def export_to_csv(self):
        """
        Export the student data to a CSV file.

        This method allows the user to save all student data
        to a CSV file. Displays a success or error message based on the outcome.
        """
        filename, _ = QFileDialog.getSaveFileName(self, "Export Students to CSV", "", "CSV Files (*.csv)")
        if filename:
            try:
                students = self.db_manager.get_all_students()
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Name", "Age", "Email", "Student ID", "Courses"])
                    for student in students:
                        courses = self.db_manager.get_courses_of_student(student['id'])
                        course_names = ', '.join([course['course_name'] for course in courses])
                        writer.writerow([student['name'], student['age'], student['email'], student['student_id'], course_names])
                QMessageBox.information(self, "Success", f"Students exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export students: {str(e)}")

class InstructorTab(QWidget):
    """
    A tab in the School Management System for managing instructors.

    This tab allows users to add, update, delete, and search for instructors. It also provides the functionality to
    export instructor data to a CSV file. The instructor data is displayed in a table view, with each instructor
    associated with their name, age, email, instructor ID, and assigned courses.

    :param parent_app: The parent application instance that provides access to shared resources such as the database manager.
    :type parent_app: SchoolManagementSystemApp
    """
    def __init__(self, parent_app):
        """
        Initialize the InstructorTab.

        This constructor sets up the interface, connects to the database manager, and creates the input fields, buttons,
        and the table for displaying instructor data.

        :param parent_app: The parent application instance that provides access to shared resources such as the database manager.
        :type parent_app: SchoolManagementSystemApp
        """
        super().__init__()
        self.app = parent_app
        self.db_manager = parent_app.db_manager
        self.init()

    def init(self):
        """
        Initialize the user interface for the InstructorTab.

        This method sets up the input fields for instructor details, the combo box for assigning courses, the buttons
        for adding, updating, deleting, and exporting instructors, and the table for displaying instructor records.
        """
        self.layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.age_input = QLineEdit()
        self.age_input.setValidator(QIntValidator(1, 150))
        self.email_input = QLineEdit()
        email_regex = QRegularExpression(r"[^@]+@[^@]+\.[^@]+")
        email_validator = QRegularExpressionValidator(email_regex)
        self.email_input.setValidator(email_validator)
        self.id_input = QLineEdit()
        self.id_input.setValidator(QIntValidator(1, 999999))

        self.course_combo = QComboBox()
        self.update_course_combo()

        form_layout.addRow(QLabel("Name:"), self.name_input)
        form_layout.addRow(QLabel("Age:"), self.age_input)
        form_layout.addRow(QLabel("Email:"), self.email_input)
        form_layout.addRow(QLabel("Instructor ID:"), self.id_input)
        form_layout.addRow(QLabel("Assign to Course:"), self.course_combo)

        self.layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Instructor")
        add_button.clicked.connect(self.add_instructor)
        update_button = QPushButton("Update Instructor")
        update_button.clicked.connect(self.update_instructor)
        delete_button = QPushButton("Delete Instructor")
        delete_button.clicked.connect(self.delete_instructor)
        export_button = QPushButton("Export to CSV")
        export_button.clicked.connect(self.export_to_csv)

        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(export_button)

        self.layout.addLayout(button_layout)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Name or ID")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_instructor)
        clear_search_button = QPushButton("Clear Search")
        clear_search_button.clicked.connect(self.update_table)

        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        search_layout.addWidget(clear_search_button)

        self.layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Age", "Email", "Instructor ID", "Courses"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellClicked.connect(self.on_table_select)

        self.layout.addWidget(self.table)

        self.update_table()

    def update_course_combo(self):
        """
        Update the course combo box with the list of available courses.

        This method retrieves the available courses from the database and updates the combo box
        to allow the user to assign the instructor to a selected course.
        """
        self.course_combo.clear()
        courses = self.db_manager.get_all_courses()
        course_names = [course['course_name'] for course in courses]
        self.course_combo.addItem("")  
        self.course_combo.addItems(course_names)

    def add_instructor(self):
        """
        Add a new instructor to the database.

        This method validates the inputs (name, age, email, and instructor ID), adds the instructor to the database,
        and optionally assigns the instructor to a selected course. Displays success or error messages.
        """
        name = self.name_input.text()
        age = self.age_input.text()
        email = self.email_input.text()
        instructor_id = self.id_input.text()
        course_name = self.course_combo.currentText()
        try:
            age = validate_numbers(age)
            validate_email(email)
            instructor_id = validate_numbers(instructor_id)

            instructor_db_id = self.db_manager.add_instructor(name, age, email, instructor_id)

            if course_name:
                course = self.db_manager.get_course_by_name(course_name)
                if course:
                    self.db_manager.assign_instructor_to_course(instructor_db_id, course['id'])

            self.app.status_bar.showMessage("Instructor added successfully.", 5000)
            self.clear_inputs()
            self.update_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_instructor(self):
        """
        Update the selected instructor's details in the database.

        This method validates the inputs (name, age, email, and instructor ID) and updates the instructor in the database.
        It also assigns the instructor to a selected course if applicable. Displays success or error messages.
        """
        if not hasattr(self, 'selected_instructor_db_id'):
            QMessageBox.warning(self, "Warning", "No instructor selected.")
            return
        name = self.name_input.text()
        age = self.age_input.text()
        email = self.email_input.text()
        instructor_id = self.id_input.text()
        course_name = self.course_combo.currentText()
        try:
            age = validate_numbers(age)
            validate_email(email)
            instructor_id = validate_numbers(instructor_id)

            self.db_manager.update_instructor(self.selected_instructor_db_id, name, age, email, instructor_id)

            if course_name:
                course = self.db_manager.get_course_by_name(course_name)
                if course:
                    self.db_manager.assign_instructor_to_course(self.selected_instructor_db_id, course['id'])

            self.app.status_bar.showMessage("Instructor updated successfully.", 5000)
            self.clear_inputs()
            self.update_table()
            del self.selected_instructor_db_id
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_instructor(self):
        """
        Delete the selected instructor from the database.

        This method prompts the user for confirmation before deleting the selected instructor. Displays success or error messages.
        """
        if not hasattr(self, 'selected_instructor_db_id'):
            QMessageBox.warning(self, "Warning", "No instructor selected.")
            return
        confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this instructor?")
        if confirm == QMessageBox.Yes:
            try:
                self.db_manager.delete_instructor(self.selected_instructor_db_id)
                self.app.status_bar.showMessage("Instructor deleted successfully.", 5000)
                self.clear_inputs()
                self.update_table()
                del self.selected_instructor_db_id
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def on_table_select(self, row, column):
        """
        Handle the event when an instructor is selected from the table.

        This method populates the input fields with the selected instructor's data, allowing the user to edit or delete
        the instructor's details.

        :param row: The row number of the selected instructor in the table.
        :type row: int
        :param column: The column number of the selected cell in the table.
        :type column: int
        """
        item = self.table.item(row, 0)
        self.selected_instructor_db_id = item.data(Qt.UserRole)
        instructor = self.db_manager.cursor.execute('SELECT * FROM instructors WHERE id = ?', (self.selected_instructor_db_id,)).fetchone()
        self.name_input.setText(instructor['name'])
        self.age_input.setText(str(instructor['age']))
        self.email_input.setText(instructor['email'])
        self.id_input.setText(str(instructor['instructor_id']))
        self.course_combo.setCurrentIndex(0)

    def clear_inputs(self):
        """
        Clear all input fields on the form.

        This method resets the name, age, email, instructor ID input fields, and the course combo box.
        """
        self.name_input.clear()
        self.age_input.clear()
        self.email_input.clear()
        self.id_input.clear()
        self.course_combo.setCurrentIndex(0)

    def update_table(self):
        """
        Update the instructor table with the latest data from the database.

        This method clears the current table and fetches all instructors from the database, populating the table with their details.
        """
        self.table.setRowCount(0)
        instructors = self.db_manager.get_all_instructors()
        for instructor in instructors:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            item = QTableWidgetItem(instructor['name'])
            item.setData(Qt.UserRole, instructor['id'])
            self.table.setItem(row_position, 0, item)
            self.table.setItem(row_position, 1, QTableWidgetItem(str(instructor['age'])))
            self.table.setItem(row_position, 2, QTableWidgetItem(instructor['email']))
            self.table.setItem(row_position, 3, QTableWidgetItem(str(instructor['instructor_id'])))
            courses = self.db_manager.get_courses_of_instructor(instructor['id'])
            course_names = ', '.join([course['course_name'] for course in courses])
            self.table.setItem(row_position, 4, QTableWidgetItem(course_names))
        self.update_course_combo()

    def search_instructor(self):
        """
        Search for instructors by name or instructor ID.

        This method fetches the instructors matching the search query and updates the table with the results.
        """
        query_text = self.search_input.text().lower()
        self.table.setRowCount(0)
        instructors = self.db_manager.search_instructors(query_text)
        for instructor in instructors:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            item = QTableWidgetItem(instructor['name'])
            item.setData(Qt.UserRole, instructor['id'])
            self.table.setItem(row_position, 0, item)
            self.table.setItem(row_position, 1, QTableWidgetItem(str(instructor['age'])))
            self.table.setItem(row_position, 2, QTableWidgetItem(instructor['email']))
            self.table.setItem(row_position, 3, QTableWidgetItem(str(instructor['instructor_id'])))
            courses = self.db_manager.get_courses_of_instructor(instructor['id'])
            course_names = ', '.join([course['course_name'] for course in courses])
            self.table.setItem(row_position, 4, QTableWidgetItem(course_names))

    def export_to_csv(self):
        """
        Export the instructor data to a CSV file.

        This method allows the user to save all instructor data
        to a CSV file. Displays a success or error message based on the outcome.
        """
        filename, _ = QFileDialog.getSaveFileName(self, "Export Instructors to CSV", "", "CSV Files (*.csv)")
        if filename:
            try:
                instructors = self.db_manager.get_all_instructors()
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Name", "Age", "Email", "Instructor ID", "Courses"])
                    for instructor in instructors:
                        courses = self.db_manager.get_courses_of_instructor(instructor['id'])
                        course_names = ', '.join([course['course_name'] for course in courses])
                        writer.writerow([instructor['name'], instructor['age'], instructor['email'], instructor['instructor_id'], course_names])
                QMessageBox.information(self, "Success", f"Instructors exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export instructors: {str(e)}")


class CourseTab(QWidget):
    """
    A tab in the School Management System for managing courses.

    This tab allows users to add, update, delete, and search for courses. It also provides the functionality to
    export course data to a CSV file. The course data is displayed in a table view, with each course
    associated with its name, course ID, assigned instructor, and enrolled students.

    :param parent_app: The parent application instance that provides access to shared resources such as the database manager.
    :type parent_app: SchoolManagementSystemApp
    """
    def __init__(self, parent_app):
        """
        Initialize the CourseTab.

        This constructor sets up the interface, connects to the database manager, and creates the input fields, buttons,
        and the table for displaying course data.

        :param parent_app: The parent application instance that provides access to shared resources such as the database manager.
        :type parent_app: SchoolManagementSystemApp
        """
        super().__init__()
        self.app = parent_app
        self.db_manager = parent_app.db_manager
        self.init()

    def init(self):
        """
        Initialize the user interface for the CourseTab.

        This method sets up the input fields for course details, the buttons for adding, updating, deleting,
        and exporting courses, and the table for displaying course records.
        """
        self.layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        self.course_name_input = QLineEdit()
        self.course_id_input = QLineEdit()
        self.course_id_input.setValidator(QIntValidator(1, 999999))

        form_layout.addRow(QLabel("Course Name:"), self.course_name_input)
        form_layout.addRow(QLabel("Course ID:"), self.course_id_input)

        self.layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Add Course")
        add_button.clicked.connect(self.add_course)
        update_button = QPushButton("Update Course")
        update_button.clicked.connect(self.update_course)
        delete_button = QPushButton("Delete Course")
        delete_button.clicked.connect(self.delete_course)
        export_button = QPushButton("Export to CSV")
        export_button.clicked.connect(self.export_to_csv)

        button_layout.addWidget(add_button)
        button_layout.addWidget(update_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(export_button)

        self.layout.addLayout(button_layout)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Name or ID")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_course)
        clear_search_button = QPushButton("Clear Search")
        clear_search_button.clicked.connect(self.update_table)

        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        search_layout.addWidget(clear_search_button)

        self.layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Course Name", "Course ID", "Instructor", "Students Enrolled"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.cellClicked.connect(self.on_table_select)

        self.layout.addWidget(self.table)

        self.update_table()

    def add_course(self):
        """
        Add a new course to the database.

        This method validates the inputs (course name and course ID) and adds the course to the database.
        Displays success or error messages.
        """
        course_name = self.course_name_input.text()
        course_id = self.course_id_input.text()
        try:
            course_id = validate_numbers(course_id)
            self.db_manager.add_course(course_name, course_id)
            self.app.status_bar.showMessage("Course added successfully.", 5000)
            self.clear_inputs()
            self.update_table()
            self.app.student_tab.update_course_combo()
            self.app.instructor_tab.update_course_combo()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def update_course(self):
        """
        Update the selected course's details in the database.

        This method validates the inputs (course name and course ID) and updates the course in the database.
        Displays success or error messages.
        """
        if not hasattr(self, 'selected_course_db_id'):
            QMessageBox.warning(self, "Warning", "No course selected.")
            return
        course_name = self.course_name_input.text()
        course_id = self.course_id_input.text()
        try:
            course_id = validate_numbers(course_id)
            self.db_manager.update_course(self.selected_course_db_id, course_name, course_id)
            self.app.status_bar.showMessage("Course updated successfully.", 5000)
            self.clear_inputs()
            self.update_table()
            self.app.student_tab.update_course_combo()
            self.app.instructor_tab.update_course_combo()
            del self.selected_course_db_id
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_course(self):
        """
        Delete the selected course from the database.

        This method prompts the user for confirmation before deleting the selected course. Displays success or error messages.
        """
        if not hasattr(self, 'selected_course_db_id'):
            QMessageBox.warning(self, "Warning", "No course selected.")
            return
        confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this course?")
        if confirm == QMessageBox.Yes:
            try:
                self.db_manager.delete_course(self.selected_course_db_id)
                self.app.status_bar.showMessage("Course deleted successfully.", 5000)
                self.clear_inputs()
                self.update_table()
                self.app.student_tab.update_course_combo()
                self.app.instructor_tab.update_course_combo()
                del self.selected_course_db_id
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def on_table_select(self, row, column):
        """
        Handle the event when a course is selected from the table.

        This method populates the input fields with the selected course's data, allowing the user to edit or delete
        the course's details.

        :param row: The row number of the selected course in the table.
        :type row: int
        :param column: The column number of the selected cell in the table.
        :type column: int
        """
        item = self.table.item(row, 0)
        self.selected_course_db_id = item.data(Qt.UserRole)
        course = self.db_manager.cursor.execute('SELECT * FROM courses WHERE id = ?', (self.selected_course_db_id,)).fetchone()
        self.course_name_input.setText(course['course_name'])
        self.course_id_input.setText(str(course['course_id']))

    def clear_inputs(self):
        """
        Clear all input fields on the form.

        This method resets the course name and course ID input fields.
        """
        self.course_name_input.clear()
        self.course_id_input.clear()

    def update_table(self):
        """
        Update the course table with the latest data from the database.

        This method clears the current table and fetches all courses from the database, populating the table with their details.
        """
        self.table.setRowCount(0)
        courses = self.db_manager.get_all_courses()
        for course in courses:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            item = QTableWidgetItem(course['course_name'])
            item.setData(Qt.UserRole, course['id'])
            self.table.setItem(row_position, 0, item)
            self.table.setItem(row_position, 1, QTableWidgetItem(str(course['course_id'])))
            instructor = self.db_manager.cursor.execute('''
                SELECT instructors.name FROM instructors
                INNER JOIN assignments ON instructors.id = assignments.instructor_id
                WHERE assignments.course_id = ?
            ''', (course['id'],)).fetchone()
            instructor_name = instructor['name'] if instructor else 'None'
            self.table.setItem(row_position, 2, QTableWidgetItem(instructor_name))
            students = self.db_manager.cursor.execute('''
                SELECT students.name FROM students
                INNER JOIN enrollments ON students.id = enrollments.student_id
                WHERE enrollments.course_id = ?
            ''', (course['id'],)).fetchall()
            student_names = ', '.join([student['name'] for student in students])
            self.table.setItem(row_position, 3, QTableWidgetItem(student_names))

    def search_course(self):
        """
        Search for courses by name or course ID.

        This method fetches the courses matching the search query and updates the table with the results.
        """
        query_text = self.search_input.text().lower()
        self.table.setRowCount(0)
        courses = self.db_manager.search_courses(query_text)
        for course in courses:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            item = QTableWidgetItem(course['course_name'])
            item.setData(Qt.UserRole, course['id'])
            self.table.setItem(row_position, 0, item)
            self.table.setItem(row_position, 1, QTableWidgetItem(str(course['course_id'])))
            instructor = self.db_manager.cursor.execute('''
                SELECT instructors.name FROM instructors
                INNER JOIN assignments ON instructors.id = assignments.instructor_id
                WHERE assignments.course_id = ?
            ''', (course['id'],)).fetchone()
            instructor_name = instructor['name'] if instructor else 'None'
            self.table.setItem(row_position, 2, QTableWidgetItem(instructor_name))
            students = self.db_manager.cursor.execute('''
                SELECT students.name FROM students
                INNER JOIN enrollments ON students.id = enrollments.student_id
                WHERE enrollments.course_id = ?
            ''', (course['id'],)).fetchall()
            student_names = ', '.join([student['name'] for student in students])
            self.table.setItem(row_position, 3, QTableWidgetItem(student_names))

    def export_to_csv(self):
        """
        Export the course data to a CSV file.

        This method allows the user to save all course data
        to a CSV file. Displays a success or error message based on the outcome.
        """
        filename, _ = QFileDialog.getSaveFileName(self, "Export Courses to CSV", "", "CSV Files (*.csv)")
        if filename:
            try:
                courses = self.db_manager.get_all_courses()
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Course Name", "Course ID", "Instructor", "Students Enrolled"])
                    for course in courses:
                        instructor = self.db_manager.cursor.execute('''
                            SELECT instructors.name FROM instructors
                            INNER JOIN assignments ON instructors.id = assignments.instructor_id
                            WHERE assignments.course_id = ?
                        ''', (course['id'],)).fetchone()
                        instructor_name = instructor['name'] if instructor else 'None'
                        students = self.db_manager.cursor.execute('''
                            SELECT students.name FROM students
                            INNER JOIN enrollments ON students.id = enrollments.student_id
                            WHERE enrollments.course_id = ?
                        ''', (course['id'],)).fetchall()
                        student_names = ', '.join([student['name'] for student in students])
                        writer.writerow([course['course_name'], course['course_id'], instructor_name, student_names])
                QMessageBox.information(self, "Success", f"Courses exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export courses: {str(e)}")

def main():
    app = QApplication(sys.argv)
    sms_app = SchoolManagementSystemApp()
    sms_app.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
