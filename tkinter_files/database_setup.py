import sqlite3
from contextlib import closing

class Database:
    """
    A class representing the database for a school management system.

    :param db_name: The name of the SQLite database file (default is 'schoolmanagementsystem.db').
    :type db_name: str
    """
    def __init__(self, db_name='schoolmanagementsystem.db'):
        self.connection = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        """
        Create the necessary tables for the system if they do not already exist.

        This method creates the following tables:
        - Students: Contains student information (student_id, name, age, email).
        - Instructors: Contains instructor information (instructor_id, name, age, email).
        - Courses: Contains course information (course_id, course_name, instructor_id).
        - Enrollments: Contains enrollment information, linking students to courses.
        - Assignments: Contains assignment information, linking instructors to courses.
        """
        with closing(self.connection.cursor()) as cursor:
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Students (
                    student_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    email TEXT NOT NULL
                )
            ''')

            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Instructors (
                    instructor_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER NOT NULL,
                    email TEXT NOT NULL
                )
            ''')

            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Courses (
                    course_id TEXT PRIMARY KEY,
                    course_name TEXT NOT NULL,
                    instructor_id TEXT,
                    FOREIGN KEY(instructor_id) REFERENCES Instructors(instructor_id)
                )
            ''')

            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Enrollments (
                    student_id TEXT,
                    course_id TEXT,
                    PRIMARY KEY (student_id, course_id),
                    FOREIGN KEY(student_id) REFERENCES Students(student_id),
                    FOREIGN KEY(course_id) REFERENCES Courses(course_id)
                )
            ''')

            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS Assignments (
                    instructor_id TEXT,
                    course_id TEXT UNIQUE,
                    PRIMARY KEY (instructor_id, course_id),
                    FOREIGN KEY(instructor_id) REFERENCES Instructors(instructor_id),
                    FOREIGN KEY(course_id) REFERENCES Courses(course_id)
                )
            ''')

            self.connection.commit()

    def close(self):
        """
        Close the database connection.
        """
        self.connection.close()
 
    def clear_all_tables(self):
        """
        Clear all data from the database tables.

        This method disables foreign key constraints, deletes all data from the 
        Enrollments, Assignments, Courses, Instructors, and Students tables, 
        and then re-enables foreign key constraints.

        :returns: 1 if the operation is successful, 0 if there is an error.
        :rtype: int
        """
        try:
            with closing(self.connection.cursor()) as cursor:
                
                cursor.execute('PRAGMA foreign_keys = OFF;')
                
                cursor.execute('DELETE FROM Enrollments;')
                cursor.execute('DELETE FROM Assignments;')
                cursor.execute('DELETE FROM Courses;')
                cursor.execute('DELETE FROM Instructors;')
                cursor.execute('DELETE FROM Students;')

                cursor.execute('PRAGMA foreign_keys = ON;')

                self.connection.commit()

            return 1
        except Exception as e:
            return 0    
