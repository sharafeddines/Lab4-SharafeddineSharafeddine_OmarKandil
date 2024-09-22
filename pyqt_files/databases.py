import sqlite3

"""
Files for managing a SQLite database for a school management system.

This module provides a `DatabaseManager` class to handle operations like:
- Adding, retrieving, updating, and deleting students, instructors, and courses.
- Enrolling students in courses and assigning instructors to courses.
- Searching records and backing up the database.
"""


class DatabaseManager:
    """
    A class to manage the SQLite database for school management.

    This class provides methods to interact with the database, including creating tables, 
    adding students, instructors, and courses, enrolling students, and assigning instructors. 
    It also supports searching and backing up the database.

    :param db_name: The name of the SQLite database file. Default is 'school_management.db'.
    :type db_name: str
    """

    def __init__(self, db_name='school_management.db'):
        """
        Initialize the database manager and create the connection.

        This constructor connects to the SQLite database and sets up the necessary tables if they do not exist.

        :param db_name: The name of the database file.
        :type db_name: str
        """
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.connection.row_factory = sqlite3.Row  
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        """
        Create the tables for the database.

        This method creates the `students`, `instructors`, `courses`, `enrollments`, 
        and `assignments` tables if they do not already exist in the database.
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                email TEXT NOT NULL UNIQUE,
                student_id INTEGER NOT NULL UNIQUE
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS instructors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                email TEXT NOT NULL UNIQUE,
                instructor_id INTEGER NOT NULL UNIQUE
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_name TEXT NOT NULL,
                course_id INTEGER NOT NULL UNIQUE
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS enrollments (
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                PRIMARY KEY (student_id, course_id),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS assignments (
                instructor_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL UNIQUE,
                PRIMARY KEY (instructor_id, course_id),
                FOREIGN KEY (instructor_id) REFERENCES instructors(id) ON DELETE SET NULL,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
        ''')

        self.connection.commit()

    def close(self):
        """
        Close the connection to the SQLite database.
        
        This method closes the database connection, ensuring that all resources are released.
        """
        self.connection.close()

    def add_student(self, name, age, email, student_id):
        """
        Add a new student to the database.

        :param name: The name of the student.
        :type name: str
        :param age: The age of the student.
        :type age: int
        :param email: The student's email address.
        :type email: str
        :param student_id: A unique identifier for the student.
        :type student_id: int
        :return: The row ID of the newly inserted student.
        :rtype: int
        """

        query = '''
            INSERT INTO students (name, age, email, student_id) VALUES (?, ?, ?, ?)
        '''
        params = (name, age, email, student_id)
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor.lastrowid

    def get_all_students(self):
        """
        Retrieve all students from the database.

        :return: A list of all students in the database.
        :rtype: list[sqlite3.Row]
        """
        query = 'SELECT * FROM students'
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_student_by_id(self, student_id):
        """
        Retrieve a student from the database by their student ID.

        :param student_id: The unique identifier of the student.
        :type student_id: int
        :return: The student record if found, or None if no student matches the ID.
        :rtype: sqlite3.Row or None
        """

        query = 'SELECT * FROM students WHERE student_id = ?'
        self.cursor.execute(query, (student_id,))
        return self.cursor.fetchone()

    def update_student(self, student_db_id, name, age, email, student_id):
        """
        Update an existing student's details in the database.

        :param student_db_id: The unique row ID of the student in the database.
        :type student_db_id: int
        :param name: The updated name of the student.
        :type name: str
        :param age: The updated age of the student.
        :type age: int
        :param email: The updated email address of the student.
        :type email: str
        :param student_id: The updated unique student identifier.
        :type student_id: int
        """

        query = '''
            UPDATE students SET name = ?, age = ?, email = ?, student_id = ? WHERE id = ?
        '''
        params = (name, age, email, student_id, student_db_id)
        self.cursor.execute(query, params)
        self.connection.commit()

    def delete_student(self, student_db_id):
        """
        Delete a student from the database by their row ID.

        :param student_db_id: The unique row ID of the student in the database.
        :type student_db_id: int
        """

        query = 'DELETE FROM students WHERE id = ?'
        self.cursor.execute(query, (student_db_id,))
        self.connection.commit()

    def add_instructor(self, name, age, email, instructor_id):
        """
        Add a new instructor to the database.

        :param name: The name of the instructor.
        :type name: str
        :param age: The age of the instructor.
        :type age: int
        :param email: The instructor's email address.
        :type email: str
        :param instructor_id: A unique identifier for the instructor.
        :type instructor_id: int
        :return: The row ID of the newly inserted instructor.
        :rtype: int
        """
        
        query = '''
            INSERT INTO instructors (name, age, email, instructor_id) VALUES (?, ?, ?, ?)
        '''
        params = (name, age, email, instructor_id)
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor.lastrowid

    def get_all_instructors(self):
        """
        Retrieve all instructors from the database.

        :return: A list of all instructors in the database.
        :rtype: list[sqlite3.Row]
        """

        query = 'SELECT * FROM instructors'
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_instructor_by_id(self, instructor_id):
        """
        Retrieve an instructor from the database by their instructor ID.

        :param instructor_id: The unique identifier of the instructor.
        :type instructor_id: int
        :return: The instructor record if found, or None if no instructor matches the ID.
        :rtype: sqlite3.Row or None
        """

        query = 'SELECT * FROM instructors WHERE instructor_id = ?'
        self.cursor.execute(query, (instructor_id,))
        return self.cursor.fetchone()

    def update_instructor(self, instructor_db_id, name, age, email, instructor_id):
        """
        Update an existing instructor's details in the database.

        :param instructor_db_id: The unique row ID of the instructor in the database.
        :type instructor_db_id: int
        :param name: The updated name of the instructor.
        :type name: str
        :param age: The updated age of the instructor.
        :type age: int
        :param email: The updated email address of the instructor.
        :type email: str
        :param instructor_id: The updated unique instructor identifier.
        :type instructor_id: int
        """

        query = '''
            UPDATE instructors SET name = ?, age = ?, email = ?, instructor_id = ? WHERE id = ?
        '''
        params = (name, age, email, instructor_id, instructor_db_id)
        self.cursor.execute(query, params)
        self.connection.commit()

    def delete_instructor(self, instructor_db_id):
        """
        Delete an instructor from the database by their row ID.

        :param instructor_db_id: The unique row ID of the instructor in the database.
        :type instructor_db_id: int
        """
        query = 'DELETE FROM instructors WHERE id = ?'
        self.cursor.execute(query, (instructor_db_id,))
        self.connection.commit()

    def add_course(self, course_name, course_id):
        """
        Add a new course to the database.

        :param course_name: The name of the course.
        :type course_name: str
        :param course_id: A unique identifier for the course.
        :type course_id: int
        :return: The row ID of the newly inserted course.
        :rtype: int
        """
        query = '''
            INSERT INTO courses (course_name, course_id) VALUES (?, ?)
        '''
        params = (course_name, course_id)
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor.lastrowid

    def get_all_courses(self):
        """
        Retrieve all courses from the database.

        :return: A list of all courses in the database.
        :rtype: list[sqlite3.Row]
        """
        query = 'SELECT * FROM courses'
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def get_course_by_name(self, course_name):
        """
        Retrieve a course from the database by its name.

        :param course_name: The name of the course.
        :type course_name: str
        :return: The course record if found, or None if no course matches the name.
        :rtype: sqlite3.Row or None
        """

        query = 'SELECT * FROM courses WHERE course_name = ?'
        self.cursor.execute(query, (course_name,))
        return self.cursor.fetchone()

    def get_course_by_id(self, course_id):
        """
        Retrieve a course from the database by its course ID.

        :param course_id: The unique identifier of the course.
        :type course_id: int
        :return: The course record if found, or None if no course matches the ID.
        :rtype: sqlite3.Row or None
        """
        query = 'SELECT * FROM courses WHERE course_id = ?'
        self.cursor.execute(query, (course_id,))
        return self.cursor.fetchone()

    def update_course(self, course_db_id, course_name, course_id):
        """
        Update an existing course's details in the database.

        :param course_db_id: The unique row ID of the course in the database.
        :type course_db_id: int
        :param course_name: The updated name of the course.
        :type course_name: str
        :param course_id: The updated unique course identifier.
        :type course_id: int
        """
        query = '''
            UPDATE courses SET course_name = ?, course_id = ? WHERE id = ?
        '''
        params = (course_name, course_id, course_db_id)
        self.cursor.execute(query, params)
        self.connection.commit()

    def delete_course(self, course_db_id):
        """
        Delete a course from the database by its row ID.

        :param course_db_id: The unique row ID of the course in the database.
        :type course_db_id: int
        """
        query = 'DELETE FROM courses WHERE id = ?'
        self.cursor.execute(query, (course_db_id,))
        self.connection.commit()

    def enroll_student_in_course(self, student_db_id, course_db_id):
        """
        Enroll a student in a course.

        :param student_db_id: The row ID of the student in the database.
        :type student_db_id: int
        :param course_db_id: The row ID of the course in the database.
        :type course_db_id: int
        """
        query = '''
            INSERT OR IGNORE INTO enrollments (student_id, course_id) VALUES (?, ?)
        '''
        params = (student_db_id, course_db_id)
        self.cursor.execute(query, params)
        self.connection.commit()

    def get_courses_of_student(self, student_db_id):
        """
        Retrieve all courses that a student is enrolled in.

        :param student_db_id: The row ID of the student in the database.
        :type student_db_id: int
        :return: A list of courses the student is enrolled in.
        :rtype: list[sqlite3.Row]
        """
        query = '''
            SELECT courses.* FROM courses
            INNER JOIN enrollments ON courses.id = enrollments.course_id
            WHERE enrollments.student_id = ?
        '''
        self.cursor.execute(query, (student_db_id,))
        return self.cursor.fetchall()

    def remove_student_enrollment(self, student_db_id, course_db_id):
        """
        Remove a student's enrollment from a course.

        :param student_db_id: The row ID of the student in the database.
        :type student_db_id: int
        :param course_db_id: The row ID of the course in the database.
        :type course_db_id: int
        """
        query = 'DELETE FROM enrollments WHERE student_id = ? AND course_id = ?'
        self.cursor.execute(query, (student_db_id, course_db_id))
        self.connection.commit()


    def assign_instructor_to_course(self, instructor_db_id, course_db_id):
        """
        Assign an instructor to a course.

        :param instructor_db_id: The row ID of the instructor in the database.
        :type instructor_db_id: int
        :param course_db_id: The row ID of the course in the database.
        :type course_db_id: int
        """
        query = '''
            INSERT OR REPLACE INTO assignments (instructor_id, course_id) VALUES (?, ?)
        '''
        params = (instructor_db_id, course_db_id)
        self.cursor.execute(query, params)
        self.connection.commit()

    def get_courses_of_instructor(self, instructor_db_id):
        """
        Retrieve all courses assigned to an instructor.

        :param instructor_db_id: The row ID of the instructor in the database.
        :type instructor_db_id: int
        :return: A list of courses assigned to the instructor.
        :rtype: list[sqlite3.Row]
        """
        query = '''
            SELECT courses.* FROM courses
            INNER JOIN assignments ON courses.id = assignments.course_id
            WHERE assignments.instructor_id = ?
        '''
        self.cursor.execute(query, (instructor_db_id,))
        return self.cursor.fetchall()

    def remove_instructor_assignment(self, course_db_id):
        """
        Remove the instructor's assignment from a course.

        :param course_db_id: The row ID of the course in the database.
        :type course_db_id: int
        """
        query = 'DELETE FROM assignments WHERE course_id = ?'
        self.cursor.execute(query, (course_db_id,))
        self.connection.commit()


    def search_students(self, search_query):
        """
        Search for students in the database by name or student ID.

        This method performs a search on the `students` table, allowing partial matches
        for the student's name or student ID using a SQL `LIKE` query.

        :param search_query: The search term to match against student names or IDs.
        :type search_query: str
        :return: A list of students matching the search query.
        :rtype: list[sqlite3.Row]
        """
        query = '''
            SELECT * FROM students
            WHERE name LIKE ? OR student_id LIKE ?
        '''
        params = (f'%{search_query}%', f'%{search_query}%')
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def search_instructors(self, search_query):
        """
        Search for instructors in the database by name or instructor ID.

        This method performs a search on the `instructors` table, allowing partial matches
        for the instructor's name or instructor ID using a SQL `LIKE` query.

        :param search_query: The search term to match against instructor names or IDs.
        :type search_query: str
        :return: A list of instructors matching the search query.
        :rtype: list[sqlite3.Row]
        """
        query = '''
            SELECT * FROM instructors
            WHERE name LIKE ? OR instructor_id LIKE ?
        '''
        params = (f'%{search_query}%', f'%{search_query}%')
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def search_courses(self, search_query):
        """
        Search for courses in the database by course name or course ID.

        This method performs a search on the `courses` table, allowing partial matches
        for the course name or course ID using a SQL `LIKE` query.

        :param search_query: The search term to match against course names or IDs.
        :type search_query: str
        :return: A list of courses matching the search query.
        :rtype: list[sqlite3.Row]
        """
        query = '''
            SELECT * FROM courses
            WHERE course_name LIKE ? OR course_id LIKE ?
        '''
        params = (f'%{search_query}%', f'%{search_query}%')
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def backup_database(self, backup_file_path):
        """
        Create a backup of the database file.

        This method closes the current database connection, copies the database file to the specified
        backup location using `shutil.copy`, and then reopens the connection.

        :param backup_file_path: The file path where the database backup should be saved.
        :type backup_file_path: str
        """
        import shutil
        self.connection.close()
        shutil.copy(self.db_name, backup_file_path)
        self.connection = sqlite3.connect(self.db_name)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
