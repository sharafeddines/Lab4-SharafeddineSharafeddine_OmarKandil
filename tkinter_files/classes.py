from contextlib import closing

from database_setup import Database

db = Database()

class Person:
    """
    A class representing a Person.

    :param name: The name of the person.
    :type name: str
    :param age: The age of the person.
    :type age: int
    :param _email: The email address of the person (treated as a protected attribute).
    :type _email: str
    """

    def __init__(self, name: str, age: int, _email: str) -> None:
        self.name = name
        self.age = age
        self._email = _email

    def get_name(self):
        """
        Get the name of the person.

        :returns: The person's name.
        :rtype: str
        """
        return self.name

    def set_name(self, value):
        """
        Set the name of the person.

        :param value: The new name of the person.
        :type value: str
        """
        self.name = value

    def get_age(self):
        """
        Get the age of the person.

        :returns: The person's age.
        :rtype: int
        """
        return self.age

    def set_age(self, value):
        """
        Set the age of the person.

        :param value: The new age of the person.
        :type value: int
        """
        self.age = value

    def get_email(self):
        """
        Get the email of the person.

        :returns: The person's email (protected attribute).
        :rtype: str
        """
        return self._email

    def introduce(self):
        """
        Print a short introduction with the person's name, age, and email.
        """
        print("Hello, I am", self.name, "and I am", self.age, "years old. My email is", self._email)

    def serialize(self):
        """
        Serialize the person object to a dictionary.

        :returns: A dictionary containing the person's details.
        :rtype: dict
        """
        return {
            'name': self.name,
            'age': self.age,
            'email': self._email
        }

    @staticmethod
    def deserialize(data):
        """
        Deserialize a dictionary into a Person object.

        :param data: A dictionary containing the person's details.
        :type data: dict
        :returns: A new instance of the Person class.
        :rtype: Person
        """
        return Person(data['name'], data['age'], data['email'])


class Student(Person):
    """
    A class representing a Student, which is a subclass of Person.

    :param name: The name of the student.
    :type name: str
    :param age: The age of the student.
    :type age: int
    :param _email: The email address of the student (inherited from Person).
    :type _email: str
    :param student_id: The unique student ID.
    :type student_id: str
    :param registered_courses: A list of registered courses for the student.
    :type registered_courses: list
    """
    def __init__(self, name: str, age: int, _email: str, student_id: str, registered_courses: list) -> None:
        super().__init__(name, age, _email)
        self.student_id = student_id
        self.registered_courses = registered_courses

    def get_student_id(self):
        """
        Get the student's ID.

        :returns: The student ID.
        :rtype: str
        """
        return self.student_id

    def set_student_id(self, student_id):
        """
        Set the student's ID.

        :param student_id: The new student ID.
        :type student_id: str
        """
        self.student_id = student_id

    def get_registered_courses(self):
        """
        Get the list of registered courses.

        :returns: A list of registered courses.
        :rtype: list
        """
        return self.registered_courses

    def set_registered_courses(self, registered_courses):
        """
        Set the registered courses for the student.

        :param registered_courses: A list of new registered courses.
        :type registered_courses: list
        """
        self.registered_courses = registered_courses

    def register_course(self, course):
        """
        Register a new course for the student.

        :param course: The course to be added.
        :type course: Course
        """
        self.registered_courses.append(course)

    def serialize(self):
        """
        Serialize the student object to a dictionary.

        :returns: A dictionary containing the student's details including registered courses.
        :rtype: dict
        """
        return {
            'name': self.name,
            'age': self.age,
            'email': self._email,
            'student_id': self.student_id,
            'registered_courses': [course.course_id for course in self.registered_courses] 
        }

    @staticmethod
    def deserialize(data, courses):
        """
        Deserialize a dictionary into a Student object.

        :param data: A dictionary containing the student's details.
        :type data: dict
        :param courses: A dictionary of course objects with course IDs as keys.
        :type courses: dict
        :returns: A new instance of the Student class.
        :rtype: Student
        """
        registered_courses = [courses[course_id] for course_id in data['registered_courses']]
        return Student(data['name'], data['age'], data['email'], data['student_id'], registered_courses)

    def save_to_db(self):
        """
        Save the student's details to the database.

        This method inserts or replaces the student's record in the Students table.
        """
        with closing(db.connection.cursor()) as cursor:
            cursor.execute('''
                INSERT OR REPLACE INTO Students (student_id, name, age, email)
                VALUES (?, ?, ?, ?)
            ''', (self.student_id, self.name, self.age, self._email))
            db.connection.commit()
    
    def edit_in_db(self):
        """
        Update the student's details in the database.

        This method updates the student's record in the Students table.
        """
        with closing(db.connection.cursor()) as cursor:
            cursor.execute('''
                UPDATE Students
                SET name = ?, age = ?, email = ?
                WHERE student_id = ?
            ''', (self.name, self.age, self._email, self.student_id))
            db.connection.commit()
    
    def handle_course_enrollment(self):
        """
        Save the student's course enrollments to the database.

        This method inserts or replaces records in the Enrollments table for the student's registered courses.
        """
        with closing(db.connection.cursor()) as cursor:
            for course in self.registered_courses:
                cursor.execute('''
                    INSERT OR REPLACE INTO Enrollments (student_id, course_id)
                    VALUES (?, ?)
                ''', (self.student_id, course.course_id))
            db.connection.commit()


class Instructor(Person):
    """
    A class representing an Instructor, which is a subclass of Person.

    :param name: The name of the instructor.
    :type name: str
    :param age: The age of the instructor.
    :type age: int
    :param _email: The email address of the instructor (inherited from Person).
    :type _email: str
    :param instructor_id: The unique ID of the instructor.
    :type instructor_id: str
    :param assigned_courses: A list of courses assigned to the instructor.
    :type assigned_courses: list
    """
    def __init__(self, name: str, age: int, _email: str, instructor_id: str, assigned_courses: list) -> None:
        super().__init__(name, age, _email)
        self.instructor_id = instructor_id
        self.assigned_courses = assigned_courses

    def get_instructor_id(self):
        """
        Get the instructor's ID.

        :returns: The instructor ID.
        :rtype: str
        """
        return self.instructor_id

    def set_instructor_id(self, instructor_id):
        """
        Set the instructor's ID.

        :param instructor_id: The new instructor ID.
        :type instructor_id: str
        """
        self.instructor_id = instructor_id

    def get_assigned_courses(self):
        """
        Get the list of assigned courses.

        :returns: A list of courses assigned to the instructor.
        :rtype: list
        """
        return self.assigned_courses

    def set_assigned_courses(self, assigned_courses):
        """
        Set the assigned courses for the instructor.

        :param assigned_courses: A new list of assigned courses.
        :type assigned_courses: list
        """
        self.assigned_courses = assigned_courses

    def assign_course(self, course):
        """
        Assign a course to the instructor and save it to the database.

        :param course: The course to assign.
        :type course: Course
        """
        self.assigned_courses.append(course)
        with closing(db.connection.cursor()) as cursor:
            cursor.execute('''
                INSERT OR REPLACE INTO Assignments (instructor_id, course_id)
                VALUES (?, ?)
            ''', (self.instructor_id, course.course_id))
            db.connection.commit()


    def serialize(self):
        """
        Serialize the instructor object to a dictionary.

        :returns: A dictionary containing the instructor's details, including assigned courses.
        :rtype: dict
        """
        return {
            'name': self.name,
            'age': self.age,
            'email': self._email,
            'instructor_id': self.instructor_id,
            'assigned_courses': [course.course_id for course in self.assigned_courses]  
        }

    @staticmethod
    def deserialize(data, courses):
        """
        Deserialize a dictionary into an Instructor object.

        :param data: A dictionary containing the instructor's details.
        :type data: dict
        :param courses: A dictionary of course objects with course IDs as keys.
        :type courses: dict
        :returns: A new instance of the Instructor class.
        :rtype: Instructor
        """
        assigned_courses = [courses[course_id] for course_id in data['assigned_courses']]
        return Instructor(data['name'], data['age'], data['email'], data['instructor_id'], assigned_courses)

    def save_to_db(self):
        """
        Save the instructor's details to the database.

        This method inserts or replaces the instructor's record in the Instructors table.
        """
        with closing(db.connection.cursor()) as cursor:
            cursor.execute('''
                INSERT OR REPLACE INTO Instructors (instructor_id, name, age, email)
                VALUES (?, ?, ?, ?)
            ''', (self.instructor_id, self.name, self.age, self._email))
            db.connection.commit()


    def edit_in_db(self):
        """
        Update the instructor's details in the database.

        This method updates the instructor's record in the Instructors table.
        """
        with closing(db.connection.cursor()) as cursor:
            cursor.execute('''
                UPDATE Instructors
                SET name = ?, age = ?, email = ?
                WHERE instructor_id = ?
            ''', (self.name, self.age, self._email, self.instructor_id))
            db.connection.commit()

    def handle_course_assignment(self):
        """
        Save the instructor's course assignments to the database.

        This method inserts or replaces records in the Assignments table for the instructor's assigned courses.
        """
        with closing(db.connection.cursor()) as cursor:
            for course in self.assigned_courses:
                cursor.execute('''
                    INSERT OR REPLACE INTO Assignments (instructor_id, course_id)
                    VALUES (?, ?)
                ''', (self.instructor_id, course.course_id))
            db.connection.commit()


class Course:
    """
    A class representing a Course.

    :param course_id: The unique identifier for the course.
    :type course_id: str
    :param course_name: The name of the course.
    :type course_name: str
    :param instructor: The instructor teaching the course.
    :type instructor: Instructor
    :param enrolled_students: A list of students enrolled in the course.
    :type enrolled_students: list
    """
    def __init__(self, course_id: str, course_name: str, instructor: Instructor, enrolled_students: list):
        self.course_id = course_id
        self.course_name = course_name
        self.instructor = instructor
        self.enrolled_students = enrolled_students

    def get_course_id(self):
        """
        Get the course ID.

        :returns: The unique course ID.
        :rtype: str
        """
        return self.course_id

    def set_course_id(self, course_id):
        """
        Set the course ID.

        :param course_id: The new course ID.
        :type course_id: str
        """
        self.course_id = course_id

    def get_course_name(self):
        """
        Get the course name.

        :returns: The name of the course.
        :rtype: str
        """
        return self.course_name

    def set_course_name(self, course_name):
        """
        Set the course name.

        :param course_name: The new course name.
        :type course_name: str
        """
        self.course_name = course_name

    def get_instructor(self):
        """
        Get the instructor of the course.

        :returns: The instructor assigned to the course.
        :rtype: Instructor
        """
        return self.instructor

    def set_instructor(self, instructor):
        """
        Set the instructor for the course.

        :param instructor: The new instructor for the course.
        :type instructor: Instructor
        """
        self.instructor = instructor

    def get_enrolled_students(self):
        """
        Get the list of enrolled students.

        :returns: A list of students enrolled in the course.
        :rtype: list
        """
        return self.enrolled_students

    def set_enrolled_students(self, enrolled_students):
        """
        Set the list of enrolled students.

        :param enrolled_students: A new list of students to enroll.
        :type enrolled_students: list
        """
        self.enrolled_students = enrolled_students

    def add_student(self, student):
        """
        Add a student to the course and update the database.

        :param student: The student to enroll in the course.
        :type student: Student
        """
        self.enrolled_students.append(student)
        with closing(db.connection.cursor()) as cursor:
            cursor.execute('''
                INSERT OR IGNORE INTO Enrollments (student_id, course_id)
                VALUES (?, ?)
            ''', (student.student_id, self.course_id))
            db.connection.commit()


    def serialize(self):
        """
        Serialize the course object to a dictionary.

        :returns: A dictionary containing the course's details, including the instructor ID and enrolled students.
        :rtype: dict
        """
        return {
            'course_id': self.course_id,
            'course_name': self.course_name,
            'instructor_id': self.instructor.instructor_id if self.instructor else None,  
            'enrolled_students': [student.student_id for student in self.enrolled_students]
        }

    @staticmethod
    def deserialize(data, instructors, students):
        """
        Deserialize a dictionary into a Course object.

        :param data: A dictionary containing the course's details.
        :type data: dict
        :param instructors: A dictionary of instructors with instructor IDs as keys.
        :type instructors: dict
        :param students: A dictionary of students with student IDs as keys.
        :type students: dict
        :returns: A new instance of the Course class.
        :rtype: Course
        """
        instructor = instructors.get(data['instructor_id'])
        enrolled_students = [students[student_id] for student_id in data['enrolled_students']]
        return Course(data['course_id'], data['course_name'], instructor, enrolled_students)

    def save_to_db(self):
        """
        Save the course's details to the database.

        This method inserts or replaces the course's record in the Courses table.
        """
        with closing(db.connection.cursor()) as cursor:
            cursor.execute('''
                INSERT OR REPLACE INTO Courses (course_id, course_name, instructor_id)
                VALUES (?, ?, ?)
            ''', (self.course_id, self.course_name, self.instructor.instructor_id if self.instructor else None))
            db.connection.commit()

    def edit_in_db(self):
        """
        Update the course's details in the database.

        This method updates the course's record in the Courses table.
        """
        with closing(db.connection.cursor()) as cursor:
            cursor.execute('''
                UPDATE Courses
                SET name = ?
                WHERE course_id = ?
            ''', (self.course_name, self.course_id))
            db.connection.commit()