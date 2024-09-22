import re

"""
School management system involving People, Students, Instructors, and Courses.

This module provides functionality to:
- Validate email addresses and numeric values.
- Define a `Person` class with `Student` and `Instructor` subclasses.
- Define a `Course` class where students can enroll and instructors can be assigned.
"""

def validate_email(email:str):
    """
    Validate an email address.

    This function uses a regular expression to check if the provided email
    address has a valid format (something like `user@example.com`).

    :param email: The email address to validate.
    :type email: str
    :raises Exception: If the email is not in a valid format or is empty.
    :return: None
    """
    email_regex = r"[^@]+@[^@]+\.[^@]+"
    if not re.match(email_regex, email) or len(email)==0:
        raise Exception("invalid email")

def validate_numbers(num:int):
    """
    Validate a numeric value to ensure it is non-negative and of type integer.

    This function checks if the input is a valid integer and that it is greater
    than zero. If the input is invalid or negative, it raises an exception.

    :param num: The number to validate.
    :type num: int
    :raises Exception: If the input is not a non-negative integer.
    :return: The validated number.
    :rtype: int
    """
    try:
        num=int(num)
    except:
        raise Exception("parameter must be non negative number")
    
    if num<=0:
        raise Exception("parameter must be non negative number")
    else:
        return num

class Person:
    """
    A class representing a Person.

    The `Person` class holds information about a person, including their name,
    age, and email address. The email and age are validated using the provided
    `validate_email` and `validate_numbers` functions.

    :param name: The name of the person.
    :type name: str
    :param age: The age of the person, must be a non-negative integer.
    :type age: int
    :param _email: The email address of the person.
    :type _email: str
    :raises Exception: If the age or email is invalid.
    """
    def __init__(self,name:str,age:int,_email:str):
        self.name=name
        age=validate_numbers(age)
        self.age=age
        validate_email(_email)
        self.email=_email

    def introduce(self):
        """
        Print an introduction of the person.

        This method prints the person's name, age, and email address.
        """
        print("Name of the person is",self.name," , their age is",self.age," and they have email:",self.email)

    def serializing_function(self):
        """
        Serialize the person's details into a dictionary.

        :return: A dictionary containing the person's name, age, and email.
        :rtype: dict
        """
        return {
            'name': self.name,
            'age': self.age,
            'email': self.email
        }
    

class Student(Person):
    """
    A class representing a Student, which is a subclass of `Person`.

    The `Student` class extends the `Person` class with additional attributes like 
    `student_id` and registered courses.

    :param name: The student's name.
    :type name: str
    :param age: The student's age, must be a non-negative integer.
    :type age: int
    :param _email: The student's email address.
    :type _email: str
    :param student_id: A unique identifier for the student.
    :type student_id: str
    :raises Exception: If the age, email, or student ID is invalid.
    """
    def __init__(self,name:str,age:int,_email:str,student_id:str):
        super().__init__(name, age, _email) 
        self.student_id=student_id
        self.registered_courses=[]
        student_id=validate_numbers(student_id)

    def register_course(self, course):
        """
        Register the student for a course.

        :param course: The course object to register for.
        :type course: Course
        :raises AssertionError: If the provided object is not of type `Course`.
        """
        assert type(course) == Course, "Must input a course"
        self.registered_courses.append(course)

class Instructor(Person):
    """
    A class representing an Instructor, which is a subclass of `Person`.

    The `Instructor` class extends the `Person` class with additional attributes like 
    `instructor_id` and assigned courses.

    :param name: The instructor's name.
    :type name: str
    :param age: The instructor's age, must be a non-negative integer.
    :type age: int
    :param _email: The instructor's email address.
    :type _email: str
    :param instructor_id: A unique identifier for the instructor.
    :type instructor_id: str
    :raises Exception: If the age, email, or instructor ID is invalid.
    """
    def __init__(self,name:str,age:int,_email:str,instructor_id:str):
        super().__init__(name, age, _email)
        self.instructor_id = instructor_id
        self.assigned_courses = [] 
        instructor_id=validate_numbers(instructor_id)

    def assign_course(self, course):
        """
        Assign the instructor to a course.

        This method assigns the instructor to a course.

        :param course: The course object to assign.
        :type course: Course
        :raises AssertionError: If the provided object is not of type `Course`.
        """
        assert type(course) == Course, "Must input a course"
        if course.instructor and course.instructor != self:
            course.instructor.assigned_courses.remove(course)
        course.instructor = self
        if course not in self.assigned_courses:
            self.assigned_courses.append(course)

class Course:
    """
    A class representing a Course.

    The `Course` class holds information about a course, including the course ID,
    name, assigned instructor, and enrolled students. It also provides methods to 
    add students to the course and serialize the course data into a dictionary.

    :param course_id: A unique identifier for the course.
    :type course_id: str
    :param course_name: The name of the course.
    :type course_name: str
    :raises Exception: If the course ID is invalid (must be a non-negative integer).
    """
    def __init__(self,course_id:str,course_name:str):
        self.course_id = course_id
        self.course_name = course_name
        self.instructor = None #initially dont have an instructor, we add it in the instructors assign course function
        self.enrolled_students =[]  
        validate_numbers(course_id)

    def add_student(self,student):
        """
        Add a student to the course.

        This method adds a student to the course's enrolled students list and registers
        the course with the student's registered courses.

        :param student: The student to add to the course.
        :type student: Student
        :raises AssertionError: If the provided object is not of type `Student`.
        :return: None
        """
        assert type(student) == Student, "Must input a student"
        self.enrolled_students.append(student)
        student.register_course(self) # we want to register the course for this student

    def serializing_function(self):
        """
        Serialize the course details into a dictionary.

        This method returns a dictionary representation of the course, including the course ID,
        name, instructor, and a list of enrolled students by their student IDs.

        :return: A dictionary containing the course details.
        :rtype: dict
        """
        return {
            'course_id': self.course_id,
            'course_name': self.course_name,
            'instructor': self.instructor.instructor_id if self.instructor else None, #(need this if since id may be none)
            'enrolled_students': [student.student_id for student in self.enrolled_students]
        }
