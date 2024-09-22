import tkinter as tk
from tkinter import ttk

from tkinter_tabs import StudentTab, InstructorTab, CourseTab, AssignInstructorTab, EnrollStudentsTab, LoadAndStoreDataTab

from classes import Student, Instructor, Course, db

from contextlib import closing

if __name__=='__main__':

    root = tk.Tk()
    notebook = ttk.Notebook(root)

    student_tab = StudentTab(notebook)
    instructor_tab = InstructorTab(notebook)
    course_tab = CourseTab(notebook)
    assign_instructor_tab = AssignInstructorTab(notebook, instructor_tab, course_tab)
    enroll_students_tab = EnrollStudentsTab(notebook, student_tab, course_tab)
    load_save_data_tab = LoadAndStoreDataTab(notebook, student_tab, instructor_tab, course_tab,  assign_instructor_tab, enroll_students_tab)
    course_tab.set_students_tab(student_tab)
    course_tab.set_instructors_tab(instructor_tab)
    instructor_tab.set_course_tab(course_tab)

    student_tab.set_enroll_students_tab(enroll_students_tab)
    course_tab.set_enroll_students_tab(enroll_students_tab)
    instructor_tab.set_assign_instructor_tab(assign_instructor_tab)
    course_tab.set_assign_instructor_tab(assign_instructor_tab)

    def load_data_from_db():
        with closing(db.connection.cursor()) as cursor:
            cursor.execute('SELECT student_id, name, age, email FROM Students')
            for row in cursor.fetchall():
                student = Student(row[1], row[2], row[3], row[0], [])
                student_tab.students.append(student)

        with closing(db.connection.cursor()) as cursor:
            cursor.execute('SELECT instructor_id, name, age, email FROM Instructors')
            for row in cursor.fetchall():
                instructor = Instructor(row[1], row[2], row[3], row[0], [])
                instructor_tab.instructors.append(instructor)

        with closing(db.connection.cursor()) as cursor:
            cursor.execute('SELECT course_id, course_name, instructor_id FROM Courses')
            for row in cursor.fetchall():
                instructor = next((inst for inst in instructor_tab.instructors if inst.instructor_id == row[2]), None)
                course = Course(row[0], row[1], instructor, [])
                course_tab.courses.append(course)
                if instructor:
                    instructor.assigned_courses.append(course)

        with closing(db.connection.cursor()) as cursor:
            cursor.execute('SELECT student_id, course_id FROM Enrollments')
            for row in cursor.fetchall():
                student = next((s for s in student_tab.students if s.student_id == row[0]), None)
                course = next((c for c in course_tab.courses if c.course_id == row[1]), None)
                if student and course:
                    student.register_course(course)
                    course.add_student(student)
        
        student_tab.update_student_treeview()
        enroll_students_tab.update_students()
        instructor_tab.update_instructor_treeview()
        assign_instructor_tab.update_instructors()
        course_tab.update_course_treeview()
        enroll_students_tab.update_courses()
        assign_instructor_tab.update_courses()
        

    load_data_from_db()


    notebook.pack(expand=True, fill='both')
    root.mainloop()