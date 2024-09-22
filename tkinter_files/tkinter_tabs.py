import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import csv
import os
import re   

from classes import Student, Instructor, Course, db

from contextlib import closing

import sqlite3

class StudentTab:
    """
    A class representing the 'Student' tab in a Tkinter notebook widget. This tab allows users to add, edit, search, and delete students, as well as view student details in a Treeview widget.

    :param notebook: The Tkinter notebook widget where the 'Student' tab will be added.
    :type notebook: ttk.Notebook
    """
    def __init__(self, notebook):
        self.students = []
        self.student_tab = ttk.Frame(notebook)
        notebook.add(self.student_tab, text="Add Student")

        form_frame = tk.Frame(self.student_tab)
        form_frame.grid(row=1, column=0, rowspan=6, padx=10, pady=10, sticky="n")

        tk.Label(form_frame, text="Student Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.student_name_entry = tk.Entry(form_frame)
        self.student_name_entry.grid(row=0, column=1, pady=2)

        tk.Label(form_frame, text="Age:").grid(row=1, column=0, sticky="w", pady=2)
        self.student_age_entry = tk.Entry(form_frame)
        self.student_age_entry.grid(row=1, column=1, pady=2)

        tk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky="w", pady=2)
        self.student_email_entry = tk.Entry(form_frame)
        self.student_email_entry.grid(row=2, column=1, pady=2)

        tk.Label(form_frame, text="Student ID:").grid(row=3, column=0, sticky="w", pady=2)
        self.student_id_entry = tk.Entry(form_frame)
        self.student_id_entry.grid(row=3, column=1, pady=2)

        tk.Button(form_frame, text="Add Student", command=self.add_student).grid(row=4, columnspan=2, pady=5)

        tk.Label(self.student_tab, text="Search:").grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.search_entry = tk.Entry(self.student_tab)
        self.search_entry.grid(row=0, column=2, padx=(5, 2), pady=5, sticky="ew")

        self.filter_criteria = tk.StringVar()
        self.filter_combobox = ttk.Combobox(self.student_tab, textvariable=self.filter_criteria, values=["Name", "Age", "Email", "ID"])
        self.filter_combobox.grid(row=0, column=3, padx=(2, 1), pady=5, sticky="ew")
        self.filter_combobox.set("Name")
        
        tk.Button(self.student_tab, text="Search", command=self.search_student).grid(row=0, column=4, padx=(1, 5), pady=5)
        tk.Button(self.student_tab, text="Clear", command=self.clear_student_search).grid(row=0, column=5, padx=(1, 5), pady=5)

        self.student_treeview = ttk.Treeview(self.student_tab, columns=("Name", "Age", "Email", "ID", "Courses"), show="headings")
        self.student_treeview.heading("Name", text="Name")
        self.student_treeview.heading("Age", text="Age")
        self.student_treeview.heading("Email", text="Email")
        self.student_treeview.heading("ID", text="Student ID")
        self.student_treeview.heading("Courses", text="Courses")
        self.student_treeview.grid(row=1, column=1, columnspan=6, rowspan=5, padx=10, pady=5, sticky='nsew')

        self.student_tab.grid_columnconfigure(2, weight=1)
        self.student_tab.grid_columnconfigure(3, weight=1)
        self.student_tab.grid_rowconfigure(1, weight=1)

        edit_button = tk.Button(self.student_tab, text="Edit Student", command=self.edit_student)
        edit_button.grid(row=0, column=6, padx=5, pady=5)

        delete_button = tk.Button(self.student_tab, text="Delete Student", command=self.delete_student)
        delete_button.grid(row=0, column=7, padx=5, pady=5)

        self.update_student_treeview()

    def add_student(self):
        """
        Add a new student to the student list and save it to the database.

        Validates the input for student name, age, email, and student ID before adding the student.
        Displays an error message if validation fails, otherwise saves the student to the database and updates the Treeview.
        """
        name = self.student_name_entry.get().strip()
        age = self.student_age_entry.get().strip()
        email = self.student_email_entry.get().strip()
        student_id = self.student_id_entry.get().strip()

        if not name or not age or not email or not student_id:
            messagebox.showerror("Error", "Please fill in all the student details.")
            return

        try:
            age = int(age)
            if age <= 0:
                messagebox.showerror("Error", "Age must be a positive integer.")
                return
        except ValueError:
            messagebox.showerror("Error", "Age must be an integer.")
            return

        email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if not email_pattern.match(email):
            messagebox.showerror("Error", "Please enter a valid email address.")
            return

        if any(s.student_id == student_id for s in self.students):
            messagebox.showerror("Error", f"A student with ID '{student_id}' already exists.")
            return

        student = Student(name, age, email, student_id, [])
        self.students.append(student)
        student.save_to_db()  
        messagebox.showinfo("Success", f"Student {name} added!")
        self.update_student_treeview()
        self.clear_form()
        self.enroll_students_tab.update_students()

    def clear_form(self):
        """
        Clear the input form fields for adding a new student.
        """
        self.student_name_entry.delete(0, tk.END)
        self.student_age_entry.delete(0, tk.END)
        self.student_email_entry.delete(0, tk.END)
        self.student_id_entry.delete(0, tk.END)

    def search_student(self):
        """
        Search for a student based on the filter criteria (Name, Age, Email, or ID) and display the results in the Treeview.
        
        If no query is provided, an error message is displayed.
        """
        for row in self.student_treeview.get_children():
            self.student_treeview.delete(row)

        query = self.search_entry.get().strip().lower()
        filter_by = self.filter_combobox.get()

        if query == "":
            messagebox.showerror("Error", "Enter search query information.")
            return

        for student in self.students:
            if filter_by == "Name" and query in student.get_name().lower():
                self.student_treeview.insert("", "end", values=(student.name, student.age, student.get_email(), student.student_id))
            elif filter_by == "ID" and query in student.get_student_id().lower():
                self.student_treeview.insert("", "end", values=(student.name, student.age, student.get_email(), student.student_id))
            elif filter_by == "Email" and query in student.get_email().lower():
                self.student_treeview.insert("", "end", values=(student.name, student.age, student.get_email(), student.student_id))
            elif filter_by == "Age" and query == str(student.get_age()).lower():
                self.student_treeview.insert("", "end", values=(student.name, student.age, student.get_email(), student.student_id))

    def clear_student_search(self):
        """
        Clear the search field and repopulate the Treeview with all students.
        """
        self.search_entry.delete(0, tk.END)
        for row in self.student_treeview.get_children():
            self.student_treeview.delete(row)

        for student in self.students:
            self.student_treeview.insert("", "end", values=(student.name, student.age, student.get_email(), student.student_id))

    def update_student_treeview(self):
        """
        Update the Treeview to display the current list of students with their assigned courses.
        """
        for row in self.student_treeview.get_children():
            self.student_treeview.delete(row)

        for student in self.students:
            courses = ", ".join(f"{course.course_name} (ID: {course.course_id})" for course in student.registered_courses)
            self.student_treeview.insert("", "end", values=(student.name, student.age, student.get_email(), student.student_id, courses))

    def set_enroll_students_tab(self, value):
        """
        Set the enroll students tab reference to allow communication between tabs.

        :param value: The reference to the enroll students tab.
        :type value: EnrollStudentsTab
        """
        self.enroll_students_tab = value

    def set_instructors_tab(self, instructors_tab):
        """
        Set the instructors tab reference to allow communication between tabs.

        :param instructors_tab: The reference to the instructors tab.
        :type instructors_tab: InstructorTab
        """
        self.instructors_tab = instructors_tab

    def set_courses_tab(self, courses_tab):
        """
        Set the courses tab reference to allow communication between tabs.

        :param courses_tab: The reference to the courses tab.
        :type courses_tab: CourseTab
        """
        self.courses_tab = courses_tab

    def set_assign_instructor_tab(self, value):
        """
        Set the assign instructor tab reference to allow communication between tabs.

        :param value: The reference to the assign instructor tab.
        :type value: AssignInstructorTab
        """
        self.assign_instructor_tab = value

    def delete_student(self):
        """
        Delete the selected student from the list and database.

        If no student is selected, an error message is displayed. Removes the student from enrolled courses and the database.
        """
        selected_item = self.student_treeview.selection()
        if selected_item:
            student_id = self.student_treeview.item(selected_item)['values'][3] 
            student = next((student for student in self.students if student.student_id == student_id), None)
            if student:
                p = [course.enrolled_students.remove(student) for course in student.registered_courses]
                self.students.remove(student)
                self.update_student_treeview()
                self.enroll_students_tab.update_students()
                with closing(db.connection.cursor()) as cursor:
                    cursor.execute('DELETE FROM Students WHERE student_id = ?', (student.student_id,))
                    cursor.execute('DELETE FROM Enrollments WHERE student_id = ?', (student.student_id,))
                    db.connection.commit()

                messagebox.showinfo("Success", "Student deleted successfully")
            else:
                messagebox.showerror("Error", "Student not found.")
        else:
            messagebox.showerror("Failed", "Select a student to delete")

    def edit_student(self):
        """
        Load the selected student's details into the form for editing.

        If no student is selected, an error message is displayed. Enables the 'Update Student' button to save changes.
        """
        selected_item = self.student_treeview.selection()
        if selected_item:
            student_id = self.student_treeview.item(selected_item)['values'][3]  
            student = next((student for student in self.students if student.student_id == student_id), None)
            if student:
                self.student_name_entry.delete(0, tk.END)
                self.student_name_entry.insert(0, student.name)
                self.student_age_entry.delete(0, tk.END)
                self.student_age_entry.insert(0, student.age)
                self.student_email_entry.delete(0, tk.END)
                self.student_email_entry.insert(0, student.get_email())
                self.student_id_entry.delete(0, tk.END)
                self.student_id_entry.insert(0, student.student_id)
                self.student_id_entry.config(state='disabled') 

                self.update_button = tk.Button(self.student_tab, text="Update Student", command=lambda: self.update_student(student_id))
                self.update_button.grid(row=6, column=1)
            else:
                messagebox.showerror("Error", "Student not found.")
        else:
            messagebox.showerror("Failed", "Select a student to edit")

    def update_student(self, student_id):
        """
        Update the selected student's details in the database and the student list.

        Validates input for name, age, and email before saving the updated student details to the database.

        :param student_id: The ID of the student to be updated.
        :type student_id: str
        """
        updated_name = self.student_name_entry.get().strip()
        updated_age = self.student_age_entry.get().strip()
        updated_email = self.student_email_entry.get().strip()

        if not updated_name or not updated_age or not updated_email:
            messagebox.showerror("Error", "Please fill in all the student details.")
            return

        try:
            updated_age = int(updated_age)
            if updated_age <= 0:
                messagebox.showerror("Error", "Age must be a positive integer.")
                return
        except ValueError:
            messagebox.showerror("Error", "Age must be an integer.")
            return

        email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if not email_pattern.match(updated_email):
            messagebox.showerror("Error", "Please enter a valid email address.")
            return

        student = next((student for student in self.students if student.student_id == student_id), None)
        if student:
            student.name = updated_name
            student.age = updated_age
            student._email = updated_email

            student.edit_in_db()
                
            self.student_name_entry.delete(0, tk.END)
            self.student_age_entry.delete(0, tk.END)
            self.student_email_entry.delete(0, tk.END)
            self.student_id_entry.config(state='normal')
            self.student_id_entry.delete(0, tk.END)

            self.update_student_treeview()
            self.enroll_students_tab.update_students()
            messagebox.showinfo("Success", "Student record updated successfully")
            self.update_button.destroy()
        else:
            messagebox.showerror("Error", "Student not found.")

class InstructorTab:
    """
    A class representing the 'Instructor' tab in a Tkinter notebook widget. This tab allows users to add, edit, search, and delete instructors, as well as view instructor details in a Treeview widget.

    :param notebook: The Tkinter notebook widget where the 'Instructor' tab will be added.
    :type notebook: ttk.Notebook
    """
    def __init__(self, notebook):
        self.instructors = []
        self.instructor_tab = ttk.Frame(notebook)
        notebook.add(self.instructor_tab, text="Add Instructor")

        form_frame = tk.Frame(self.instructor_tab)
        form_frame.grid(row=1, column=0, rowspan=6, padx=10, pady=10, sticky="n")

        tk.Label(form_frame, text="Instructor Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.instructor_name_entry = tk.Entry(form_frame)
        self.instructor_name_entry.grid(row=0, column=1, pady=2)

        tk.Label(form_frame, text="Age:").grid(row=1, column=0, sticky="w", pady=2)
        self.instructor_age_entry = tk.Entry(form_frame)
        self.instructor_age_entry.grid(row=1, column=1, pady=2)

        tk.Label(form_frame, text="Email:").grid(row=2, column=0, sticky="w", pady=2)
        self.instructor_email_entry = tk.Entry(form_frame)
        self.instructor_email_entry.grid(row=2, column=1, pady=2)

        tk.Label(form_frame, text="Instructor ID:").grid(row=3, column=0, sticky="w", pady=2)
        self.instructor_id_entry = tk.Entry(form_frame)
        self.instructor_id_entry.grid(row=3, column=1, pady=2)

        tk.Button(form_frame, text="Add Instructor", command=self.add_instructor).grid(row=4, columnspan=2, pady=5)

        tk.Label(self.instructor_tab, text="Search:").grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.search_entry = tk.Entry(self.instructor_tab)
        self.search_entry.grid(row=0, column=2, padx=(5, 2), pady=5, sticky="ew")

        self.filter_criteria = tk.StringVar()
        self.filter_combobox = ttk.Combobox(self.instructor_tab, textvariable=self.filter_criteria, values=["Name", "Age", "Email", "ID"])
        self.filter_combobox.grid(row=0, column=3, padx=(2, 1), pady=5, sticky="ew")
        self.filter_combobox.set("Name") 


        tk.Button(self.instructor_tab, text="Search", command=self.search_instructor).grid(row=0, column=4, padx=(1, 5), pady=5)
        tk.Button(self.instructor_tab, text="Clear", command=self.clear_instructor_search).grid(row=0, column=5, padx=(1, 5), pady=5)

        self.instructor_treeview = ttk.Treeview(self.instructor_tab, columns=("Name", "Age", "Email", "ID", "Assigned Courses"), show="headings")
        self.instructor_treeview.heading("Name", text="Name")
        self.instructor_treeview.heading("Age", text="Age")
        self.instructor_treeview.heading("Email", text="Email")
        self.instructor_treeview.heading("ID", text="Instructor ID")
        self.instructor_treeview.heading("Assigned Courses", text="Assigned Courses")
        self.instructor_treeview.grid(row=1, column=1, columnspan=6, rowspan=5, padx=10, pady=5, sticky='nsew')

        self.instructor_tab.grid_columnconfigure(2, weight=1)
        self.instructor_tab.grid_columnconfigure(3, weight=1)
        self.instructor_tab.grid_rowconfigure(1, weight=1)

        edit_button = tk.Button(self.instructor_tab, text="Edit Instructor", command=self.edit_instructor)
        edit_button.grid(row=0, column=6, padx=5, pady=5)

        delete_button = tk.Button(self.instructor_tab, text="Delete Instructor", command=self.delete_instructor)
        delete_button.grid(row=0, column=7, padx=5, pady=5)

        self.update_instructor_treeview()

    def add_instructor(self):
        """
        Add a new instructor to the instructor list and save it to the database.

        Validates the input for instructor name, age, email, and instructor ID before adding the instructor.
        Displays an error message if validation fails, otherwise saves the instructor to the database and updates the Treeview.
        """
        name = self.instructor_name_entry.get().strip()
        age = self.instructor_age_entry.get().strip()
        email = self.instructor_email_entry.get().strip()
        instructor_id = self.instructor_id_entry.get().strip()

        if not name or not age or not email or not instructor_id:
            messagebox.showerror("Error", "Please fill in all the instructor details.")
            return

        try:
            age = int(age)
            if age <= 0:
                messagebox.showerror("Error", "Age must be a positive integer.")
                return
        except ValueError:
            messagebox.showerror("Error", "Age must be an integer.")
            return

        email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if not email_pattern.match(email):
            messagebox.showerror("Error", "Please enter a valid email address.")
            return

        if any(inst.instructor_id == instructor_id for inst in self.instructors):
            messagebox.showerror("Error", f"An instructor with ID '{instructor_id}' already exists.")
            return

        instructor = Instructor(name, age, email, instructor_id, [])
        self.instructors.append(instructor)
        instructor.save_to_db()  
        messagebox.showinfo("Success", f"Instructor {name} added!")
        self.update_instructor_treeview()
        self.clear_form()
        self.assign_instructor_tab.update_instructors()

    def clear_form(self):
        """
        Clear the input form fields for adding a new instructor.
        """
        self.instructor_name_entry.delete(0, tk.END)
        self.instructor_age_entry.delete(0, tk.END)
        self.instructor_email_entry.delete(0, tk.END)
        self.instructor_id_entry.delete(0, tk.END)

    def search_instructor(self):
        """
        Search for an instructor based on the filter criteria (Name, Age, Email, or ID) and display the results in the Treeview.

        If no query is provided, an error message is displayed.
        """
        for row in self.instructor_treeview.get_children():
            self.instructor_treeview.delete(row)

        query = self.search_entry.get().strip().lower()
        filter_by = self.filter_combobox.get()

        if query == "":
            messagebox.showerror("Error", "Enter search query information.")
            return

        for instructor in self.instructors:
            if filter_by == "Name" and query in instructor.get_name().lower():
                self.insert_instructor_into_treeview(instructor)
            elif filter_by == "ID" and query in instructor.get_instructor_id().lower():
                self.insert_instructor_into_treeview(instructor)
            elif filter_by == "Email" and query in instructor.get_email().lower():
                self.insert_instructor_into_treeview(instructor)
            elif filter_by == "Age" and query == str(instructor.get_age()).lower():
                self.insert_instructor_into_treeview(instructor)

    def insert_instructor_into_treeview(self, instructor):
        """
        Insert an instructor's details into the Treeview widget.

        :param instructor: The instructor object to be inserted into the Treeview.
        :type instructor: Instructor
        """
        courses = ", ".join(f"{course.course_name} (ID: {course.course_id})" for course in instructor.assigned_courses)
        self.instructor_treeview.insert("", "end", values=(instructor.name, instructor.age, instructor.get_email(), instructor.instructor_id, courses))

    def clear_instructor_search(self):
        """
        Clear the search field and repopulate the Treeview with all instructors.
        """
        self.search_entry.delete(0, tk.END)
        for row in self.instructor_treeview.get_children():
            self.instructor_treeview.delete(row)

        for instructor in self.instructors:
            self.insert_instructor_into_treeview(instructor)

    def update_instructor_treeview(self):
        """
        Update the Treeview to display the current list of instructors with their assigned courses.
        """
        for row in self.instructor_treeview.get_children():
            self.instructor_treeview.delete(row)

        for instructor in self.instructors:
            self.insert_instructor_into_treeview(instructor)

    def set_assign_instructor_tab(self, value):
        """
        Set the assign instructor tab reference to allow communication between tabs.

        :param value: The reference to the assign instructor tab.
        :type value: AssignInstructorTab
        """
        self.assign_instructor_tab = value

    def delete_instructor(self):
        """
        Delete the selected instructor from the list and database.

        If no instructor is selected, an error message is displayed. Removes the instructor from the assigned courses and the database.
        """
        selected_item = self.instructor_treeview.selection()
        if selected_item:
            instructor_id = self.instructor_treeview.item(selected_item)['values'][3]  
            instructor = next((instructor for instructor in self.instructors if instructor.instructor_id == instructor_id), None)
            if instructor:
                for course in instructor.assigned_courses:
                    course.set_instructor(None)
                self.instructors.remove(instructor)
                self.update_instructor_treeview()
                self.course_tab.update_course_treeview()
                self.assign_instructor_tab.update_instructors()
                with closing(db.connection.cursor()) as cursor:
                    cursor.execute('DELETE FROM Instructors WHERE instructor_id = ?', (instructor.instructor_id,))
                    cursor.execute('DELETE FROM Assignments WHERE instructor_id = ?', (instructor.instructor_id,))
                    db.connection.commit()
                messagebox.showinfo("Success", "Instructor deleted successfully")
            else:
                messagebox.showerror("Error", "Instructor not found.")
        else:
            messagebox.showerror("Failed", "Select an instructor to delete")

    def edit_instructor(self):
        """
        Load the selected instructor's details into the form for editing.

        If no instructor is selected, an error message is displayed. Enables the 'Update Instructor' button to save changes.
        """
        selected_item = self.instructor_treeview.selection()
        if selected_item:
            instructor_id = self.instructor_treeview.item(selected_item)['values'][3]  
            instructor = next((instructor for instructor in self.instructors if instructor.instructor_id == instructor_id), None)
            if instructor:
                
                self.instructor_name_entry.delete(0, tk.END)
                self.instructor_name_entry.insert(0, instructor.name)
                self.instructor_age_entry.delete(0, tk.END)
                self.instructor_age_entry.insert(0, instructor.age)
                self.instructor_email_entry.delete(0, tk.END)
                self.instructor_email_entry.insert(0, instructor.get_email())
                self.instructor_id_entry.delete(0, tk.END)
                self.instructor_id_entry.insert(0, instructor.instructor_id)
                self.instructor_id_entry.config(state='disabled')  

                
                self.update_button = tk.Button(self.instructor_tab, text="Update Instructor", command=lambda: self.update_instructor(instructor_id))
                self.update_button.grid(row=6, column=1)
            else:
                messagebox.showerror("Error", "Instructor not found.")
        else:
            messagebox.showerror("Failed", "Select an instructor to edit")

    def update_instructor(self, instructor_id):
        """
        Update the selected instructor's details in the database and the instructor list.

        Validates input for name, age, and email before saving the updated instructor details to the database.
        
        :param instructor_id: The ID of the instructor to be updated.
        :type instructor_id: str
        """
        updated_name = self.instructor_name_entry.get().strip()
        updated_age = self.instructor_age_entry.get().strip()
        updated_email = self.instructor_email_entry.get().strip()

        if not updated_name or not updated_age or not updated_email:
            messagebox.showerror("Error", "Please fill in all the instructor details.")
            return

        try:
            updated_age = int(updated_age)
            if updated_age <= 0:
                messagebox.showerror("Error", "Age must be a positive integer.")
                return
        except ValueError:
            messagebox.showerror("Error", "Age must be an integer.")
            return

        email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if not email_pattern.match(updated_email):
            messagebox.showerror("Error", "Please enter a valid email address.")
            return

        instructor = next((inst for inst in self.instructors if inst.instructor_id == instructor_id), None)
        if instructor:
            instructor.name = updated_name
            instructor.age = updated_age
            instructor._email = updated_email

            instructor.edit_in_db()

            self.instructor_name_entry.delete(0, tk.END)
            self.instructor_age_entry.delete(0, tk.END)
            self.instructor_email_entry.delete(0, tk.END)
            self.instructor_id_entry.config(state='normal')
            self.instructor_id_entry.delete(0, tk.END)

            self.update_instructor_treeview()
            self.assign_instructor_tab.update_instructors()
            self.course_tab.update_course_treeview()
            messagebox.showinfo("Success", "Instructor record updated successfully")
            self.update_button.destroy()
        else:
            messagebox.showerror("Error", "Instructor not found.")

    def set_course_tab(self, course_tab):
        """
        Set the course tab reference to allow communication between tabs.

        :param course_tab: The reference to the course tab.
        :type course_tab: CourseTab
        """
        self.course_tab = course_tab

class CourseTab:
    """
    A class representing the 'Course' tab in a Tkinter notebook widget. This tab allows users to add, edit, search, and delete courses, as well as view course details in a Treeview widget.

    :param notebook: The Tkinter notebook widget where the 'Course' tab will be added.
    :type notebook: ttk.Notebook
    """
    def __init__(self, notebook):
        self.courses = []
        self.course_tab = ttk.Frame(notebook)
        notebook.add(self.course_tab, text="Add Course")

        form_frame = tk.Frame(self.course_tab)
        form_frame.grid(row=1, column=0, rowspan=6, padx=10, pady=10, sticky="n")

        tk.Label(form_frame, text="Course Name:").grid(row=0, column=0, sticky="w", pady=2)
        self.course_name_entry = tk.Entry(form_frame)
        self.course_name_entry.grid(row=0, column=1, pady=2)

        tk.Label(form_frame, text="Course ID:").grid(row=1, column=0, sticky="w", pady=2)
        self.course_id_entry = tk.Entry(form_frame)
        self.course_id_entry.grid(row=1, column=1, pady=2)

        tk.Button(form_frame, text="Add Course", command=self.add_course).grid(row=4, columnspan=2, pady=5)

        tk.Label(self.course_tab, text="Search:").grid(row=0, column=1, padx=5, pady=5, sticky='w')
        self.search_entry = tk.Entry(self.course_tab)
        self.search_entry.grid(row=0, column=2, padx=(5, 2), pady=5, sticky="ew")

        self.filter_criteria = tk.StringVar()
        self.filter_combobox = ttk.Combobox(self.course_tab, textvariable=self.filter_criteria, values=["Course Name", "Course ID"])
        self.filter_combobox.grid(row=0, column=3, padx=(2, 1), pady=5, sticky="ew")
        self.filter_combobox.set("Course Name") 

        tk.Button(self.course_tab, text="Search", command=self.search_course).grid(row=0, column=4, padx=(1, 5), pady=5)
        tk.Button(self.course_tab, text="Clear", command=self.clear_course_search).grid(row=0, column=5, padx=(1, 5), pady=5)

        self.course_treeview = ttk.Treeview(self.course_tab, columns=("Course Name", "Course ID", "Instructor"), show="headings")
        self.course_treeview.heading("Course Name", text="Course Name")
        self.course_treeview.heading("Course ID", text="Course ID")
        self.course_treeview.heading("Instructor", text="Instructor")
        self.course_treeview.grid(row=1, column=1, columnspan=6, rowspan=5, padx=10, pady=5, sticky='nsew')

        self.course_tab.grid_columnconfigure(2, weight=1)
        self.course_tab.grid_columnconfigure(3, weight=1)
        self.course_tab.grid_rowconfigure(1, weight=1)

        edit_button = tk.Button(self.course_tab, text="Edit Course", command=self.edit_course)
        edit_button.grid(row=0, column=6, padx=5, pady=5)

        delete_button = tk.Button(self.course_tab, text="Delete Course", command=self.delete_course)
        delete_button.grid(row=0, column=7, padx=5, pady=5)

        self.update_course_treeview()

    def add_course(self):
        """
        Add a new course to the course list and save it to the database.

        Validates the input for course name and course ID before adding the course.
        Displays an error message if validation fails, otherwise saves the course to the database and updates the Treeview.
        """
        course_name = self.course_name_entry.get().strip()
        course_id = self.course_id_entry.get().strip()

        if not course_name or not course_id:
            messagebox.showerror("Error", "Please fill in all the course details.")
            return

        if any(course.course_id == course_id for course in self.courses):
            messagebox.showerror("Error", f"A course with ID '{course_id}' already exists.")
            return

        if not re.match(r"^[A-Za-z0-9]+$", course_id):
            messagebox.showerror("Error", "Course ID should be alphanumeric without spaces.")
            return

        if not re.match(r"^[A-Za-z0-9 ]+$", course_name):
            messagebox.showerror("Error", "Course Name should contain only letters, numbers, and spaces.")
            return

        course = Course(course_id, course_name, None, [])
        self.courses.append(course)
        course.save_to_db()  
        messagebox.showinfo("Success", f"Course '{course_name}' added!")
        self.update_course_treeview()
        self.clear_form()
        self.assign_instructor_tab.update_courses()
        self.enroll_students_tab.update_courses()

    def clear_form(self):
        """
        Clear the input form fields for adding a new course.
        """
        self.course_name_entry.delete(0, tk.END)
        self.course_id_entry.delete(0, tk.END)

    def search_course(self):
        """
        Search for a course based on the filter criteria (Course Name or Course ID) and display the results in the Treeview.

        If no query is provided, an error message is displayed.
        """
        for row in self.course_treeview.get_children():
            self.course_treeview.delete(row)

        query = self.search_entry.get().strip().lower()
        filter_by = self.filter_combobox.get()

        if query == "":
            messagebox.showerror("Error", "Enter search query information.")
            return

        for course in self.courses:
            if filter_by == "Course Name" and query in course.get_course_name().lower():
                self.insert_course_into_treeview(course)
            elif filter_by == "Course ID" and query in course.get_course_id().lower():
                self.insert_course_into_treeview(course)

    def clear_course_search(self):
        """
        Clear the search field and repopulate the Treeview with all courses.
        """
        self.search_entry.delete(0, tk.END)
        for row in self.course_treeview.get_children():
            self.course_treeview.delete(row)

        for course in self.courses:
            self.insert_course_into_treeview(course)

    def update_course_treeview(self):
        """
        Update the Treeview to display the current list of courses with their assigned instructors.
        """
        for row in self.course_treeview.get_children():
            self.course_treeview.delete(row)

        for course in self.courses:
            self.insert_course_into_treeview(course)

    def insert_course_into_treeview(self, course):
        """
        Insert a course's details into the Treeview widget.

        :param course: The course object to be inserted into the Treeview.
        :type course: Course
        """
        instructor_name = course.get_instructor().get_name() if course.get_instructor() else ""
        self.course_treeview.insert("", "end", values=(course.get_course_name(), course.get_course_id(), instructor_name))

    def set_assign_instructor_tab(self, value):
        """
        Set the assign instructor tab reference to allow communication between tabs.

        :param value: The reference to the assign instructor tab.
        :type value: AssignInstructorTab
        """
        self.assign_instructor_tab = value

    def set_enroll_students_tab(self, value):
        """
        Set the enroll students tab reference to allow communication between tabs.

        :param value: The reference to the enroll students tab.
        :type value: EnrollStudentsTab
        """
        self.enroll_students_tab = value

    def delete_course(self):
        """
        Delete the selected course from the list and database.

        If no course is selected, an error message is displayed. Removes the course from enrolled students and the database.
        """
        selected_item = self.course_treeview.selection()
        if selected_item:
            course_id = self.course_treeview.item(selected_item)['values'][1] 
            course = next((course for course in self.courses if course.course_id == course_id), None)
            if course:
                for student in course.enrolled_students:
                    if course in student.registered_courses:
                        student.registered_courses.remove(course)
                
                if course.instructor and course in course.instructor.assigned_courses:
                    course.instructor.assigned_courses.remove(course)
                self.courses.remove(course)
                self.update_course_treeview()
                self.enroll_students_tab.update_courses()
                self.assign_instructor_tab.update_courses()
                self.students_tab.update_student_treeview()
                self.instructors_tab.update_instructor_treeview()
                with closing(db.connection.cursor()) as cursor:
                    cursor.execute('DELETE FROM Courses WHERE course_id = ?', (course.course_id,))
                    cursor.execute('DELETE FROM Enrollments WHERE course_id = ?', (course.course_id,))
                    cursor.execute('DELETE FROM Assignments WHERE course_id = ?', (course.course_id,))
                    db.connection.commit()

                messagebox.showinfo("Success", "Course deleted successfully")
            else:
                messagebox.showerror("Error", "Course not found.")
        else:
            messagebox.showerror("Failed", "Select a course to delete")

    def edit_course(self):
        """
        Load the selected course's details into the form for editing.

        If no course is selected, an error message is displayed. Enables the 'Update Course' button to save changes.
        """
        selected_item = self.course_treeview.selection()
        if selected_item:
            course_id = self.course_treeview.item(selected_item)['values'][1]  
            course = next((course for course in self.courses if course.course_id == course_id), None)
            if course:
                
                self.course_name_entry.delete(0, tk.END)
                self.course_name_entry.insert(0, course.course_name)
                self.course_id_entry.delete(0, tk.END)
                self.course_id_entry.insert(0, course.course_id)
                self.course_id_entry.config(state='disabled')  
                self.update_button = tk.Button(self.course_tab, text="Update Course", command=lambda: self.update_course(course_id))
                self.update_button.grid(row=6, column=1)
            else:
                messagebox.showerror("Error", "Course not found.")
        else:
            messagebox.showerror("Failed", "Select a course to edit")

    def update_course(self, course_id):
        """
        Update the selected course's details in the database and the course list.

        Validates input for the course name before saving the updated course details to the database.

        :param course_id: The ID of the course to be updated.
        :type course_id: str
        """
        updated_name = self.course_name_entry.get().strip()

        if not updated_name:
            messagebox.showerror("Error", "Please enter the course name.")
            return

        if not re.match(r"^[A-Za-z0-9 ]+$", updated_name):
            messagebox.showerror("Error", "Course Name should contain only letters, numbers, and spaces.")
            return

        course = next((course for course in self.courses if course.course_id == course_id), None)
        if course:
            course.course_name = updated_name

            course.edit_in_db()
            
            self.course_name_entry.delete(0, tk.END)
            self.course_id_entry.config(state='normal')
            self.course_id_entry.delete(0, tk.END)

            self.update_course_treeview()
            self.enroll_students_tab.update_courses()
            self.assign_instructor_tab.update_courses()
            self.students_tab.update_student_treeview()
            self.instructors_tab.update_instructor_treeview()
            messagebox.showinfo("Success", "Course record updated successfully")
            self.update_button.destroy()
        else:
            messagebox.showerror("Error", "Course not found.")

    def set_students_tab(self, value):
        """
        Set the students tab reference to allow communication between tabs.

        :param value: The reference to the students tab.
        :type value: StudentTab
        """
        self.students_tab = value

    def set_instructors_tab(self, value):
        """
        Set the instructors tab reference to allow communication between tabs.

        :param value: The reference to the instructors tab.
        :type value: InstructorTab
        """
        self.instructors_tab = value

class AssignInstructorTab:
    """
    A class for assigning instructors to courses in a Tkinter notebook widget. This tab allows users to select an instructor and a course, then assign the instructor to the course.

    :param notebook: The Tkinter notebook widget where the 'Assign Instructor' tab will be added.
    :type notebook: ttk.Notebook
    :param instructors_tab: The reference to the instructors tab.
    :type instructors_tab: InstructorTab
    :param courses_tab: The reference to the courses tab.
    :type courses_tab: CourseTab
    """
    def __init__(self, notebook, instructors_tab, courses_tab):
        self.frame = ttk.Frame(notebook)
        self.instructors_tab = instructors_tab
        self.courses_tab = courses_tab
        self.instructor_var = tk.StringVar()
        self.course_var = tk.StringVar()
        
        notebook.add(self.frame, text="Assign Instructor")

        ttk.Label(self.frame, text="Select Instructor").grid(row=0, column=0, padx=10, pady=10)
        self.instructor_menu = ttk.Combobox(self.frame, textvariable=self.instructor_var, state="readonly")
        self.instructor_menu.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.frame, text="Select Course").grid(row=1, column=0, padx=10, pady=10)
        self.course_menu = ttk.Combobox(self.frame, textvariable=self.course_var, state="readonly")
        self.course_menu.grid(row=1, column=1, padx=10, pady=10)

        self.assign_button = ttk.Button(self.frame, text="Assign Instructor", command=self.assign_instructor)
        self.assign_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.instructor_list = []
        self.course_list = []

        self.populate_dropdowns()

    def populate_dropdowns(self):
        """
        Populate the dropdown menus with available instructors and courses that don't have an assigned instructor.

        Sets the values for both the instructor dropdown and the course dropdown. Disables the assign button if no instructors or courses are available.
        """
        self.instructor_list = self.instructors_tab.instructors
        all_courses = self.courses_tab.courses
        print(all_courses)
        instructor_display = [f"{inst.name} (ID: {inst.instructor_id})" for inst in self.instructor_list]

        self.course_list = [course for course in all_courses if course.instructor is None]
        course_display = [f"{course.course_name} (ID: {course.course_id})" for course in self.course_list]
        print(course_display)
        self.instructor_menu['values'] = instructor_display
        self.course_menu['values'] = course_display

        if not self.instructor_list or not self.course_list:
            self.assign_button.config(state='disabled')
        else:
            self.assign_button.config(state='normal')

    def assign_instructor(self):
        """
        Assign the selected instructor to the selected course.

        Validates the selections and checks if the course is already assigned to an instructor. If successful, the instructor is assigned to the course and the Treeviews are updated.
        Displays success or error messages based on the result.

        :raises ValueError: If the selection of an instructor or course is invalid.
        """
        instructor_selection = self.instructor_var.get()
        course_selection = self.course_var.get()

        if not instructor_selection or not course_selection:
            messagebox.showwarning("Input Error", "Please select both an instructor and a course.")
            return

        try:
            instructor_index = self.instructor_menu.current()
            selected_instructor = self.instructor_list[instructor_index]
        except (IndexError, ValueError):
            messagebox.showerror("Selection Error", "Invalid instructor selected.")
            return

        try:
            course_index = self.course_menu.current()
            selected_course = self.course_list[course_index]
        except (IndexError, ValueError):
            messagebox.showerror("Selection Error", "Invalid course selected.")
            return

        if selected_course.instructor is not None:
            current_instructor = selected_course.instructor
            messagebox.showerror("Error", f"The course '{selected_course.course_name}' is already assigned to instructor '{current_instructor.name}' (ID: {current_instructor.instructor_id}).")
            self.populate_dropdowns() 
            return

        selected_course.set_instructor(selected_instructor)
        selected_instructor.assign_course(selected_course)

        self.instructors_tab.update_instructor_treeview()
        self.courses_tab.update_course_treeview()

        self.instructor_var.set('')
        self.course_var.set('')

        self.populate_dropdowns()

        messagebox.showinfo("Success", f"Instructor '{selected_instructor.name}' assigned to course '{selected_course.course_name}' successfully!")

    def update_instructors(self):
        """
        Update the instructor dropdown when there are changes in the list of available instructors.

        Calls `populate_dropdowns()` to refresh the list of instructors.
        """
        self.populate_dropdowns()

    def update_courses(self):
        """
        Update the course dropdown when there are changes in the list of available courses.

        Calls `populate_dropdowns()` to refresh the list of courses.
        """
        self.populate_dropdowns()

class EnrollStudentsTab:
    """
    A class for enrolling students in courses in a Tkinter notebook widget. This tab allows users to select a student and a course, then enroll the student in the course.

    :param notebook: The Tkinter notebook widget where the 'Enroll Students' tab will be added.
    :type notebook: ttk.Notebook
    :param students_tab: The reference to the students tab.
    :type students_tab: StudentTab
    :param courses_tab: The reference to the courses tab.
    :type courses_tab: CourseTab
    """
    def __init__(self, notebook, students_tab, courses_tab):
        self.frame = ttk.Frame(notebook)
        self.students_tab = students_tab
        self.courses_tab = courses_tab
        self.student_var = tk.StringVar()
        self.course_var = tk.StringVar()
        
        notebook.add(self.frame, text="Enroll Student")

        ttk.Label(self.frame, text="Select Student").grid(row=0, column=0, padx=10, pady=10)
        self.student_menu = ttk.Combobox(self.frame, textvariable=self.student_var, state="readonly")
        self.student_menu.grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(self.frame, text="Select Course").grid(row=1, column=0, padx=10, pady=10)
        self.course_menu = ttk.Combobox(self.frame, textvariable=self.course_var, state="readonly")
        self.course_menu.grid(row=1, column=1, padx=10, pady=10)

        self.enroll_button = ttk.Button(self.frame, text="Enroll Student", command=self.enroll_student)
        self.enroll_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.student_list = []
        self.course_list = []

        self.populate_dropdowns()

    def populate_dropdowns(self):
        """
        Populate the dropdown menus with available students and courses.

        Displays students and courses that the selected student is not already enrolled in. Updates the dropdown menus for students and courses. Disables the enroll button if there are no students or courses available for selection.
        """
        self.student_list = self.students_tab.students
        all_courses = self.courses_tab.courses

        student_display = [f"{student.name} (ID: {student.student_id})" for student in self.student_list]

        self.course_list = []
        selected_student_index = self.student_menu.current()
        if selected_student_index != -1:
            selected_student = self.student_list[selected_student_index]
            self.course_list = [course for course in all_courses if course not in selected_student.registered_courses]
        else:
            self.course_list = all_courses

        course_display = [f"{course.course_name} (ID: {course.course_id})" for course in self.course_list]

        self.student_menu['values'] = student_display
        self.course_menu['values'] = course_display

        if not self.student_list or not self.course_list:
            self.enroll_button.config(state='disabled')
        else:
            self.enroll_button.config(state='normal')

    def enroll_student(self):
        """
        Enroll the selected student in the selected course.

        Validates the selections to ensure a student and a course are selected, checks if the student is already enrolled in the course or an equivalent course, and if successful, enrolls the student in the course and updates the Treeviews.
        Displays success or error messages based on the result.

        :raises ValueError: If the selection of a student or course is invalid.
        """
        student_selection = self.student_var.get()
        course_selection = self.course_var.get()

        if not student_selection or not course_selection:
            messagebox.showwarning("Input Error", "Please select both a student and a course.")
            return

        try:
            student_index = self.student_menu.current()
            selected_student = self.student_list[student_index]
        except (IndexError, ValueError):
            messagebox.showerror("Selection Error", "Invalid student selected.")
            return

        try:
            course_index = self.course_menu.current()
            selected_course = self.course_list[course_index]
        except (IndexError, ValueError):
            messagebox.showerror("Selection Error", "Invalid course selected.")
            return

        if selected_course in selected_student.registered_courses:
            messagebox.showwarning("Input Error", f"Student '{selected_student.name}' is already enrolled in course '{selected_course.course_name}'.")
            self.populate_dropdowns()
            return

        if any(course.course_name == selected_course.course_name for course in selected_student.registered_courses):
            messagebox.showwarning("Input Error", f"Student '{selected_student.name}' is already enrolled in an equivalent course '{selected_course.course_name}'.")
            self.populate_dropdowns()
            return

        selected_course.add_student(selected_student)
        selected_student.register_course(selected_course)

        self.students_tab.update_student_treeview()
        self.courses_tab.update_course_treeview()

        self.course_var.set('')
        self.populate_dropdowns()

        messagebox.showinfo("Success", f"Student '{selected_student.name}' enrolled in course '{selected_course.course_name}' successfully!")

    def update_students(self):
        """
        Update the student dropdown when there are changes in the list of available students.

        Calls `populate_dropdowns()` to refresh the list of students.
        """
        self.populate_dropdowns()

    def update_courses(self):
        """
        Update the course dropdown when there are changes in the list of available courses.

        Calls `populate_dropdowns()` to refresh the list of courses.
        """
        self.populate_dropdowns()

class LoadAndStoreDataTab:
    """
    A class for managing data in a Tkinter notebook widget. This tab allows users to load, save, and back up data for students, instructors, and courses in both JSON and CSV formats.

    :param notebook: The Tkinter notebook widget where the 'Manage Data' tab will be added.
    :type notebook: ttk.Notebook
    :param student_tab: The reference to the students tab.
    :type student_tab: StudentTab
    :param instructor_tab: The reference to the instructors tab.
    :type instructor_tab: InstructorTab
    :param course_tab: The reference to the courses tab.
    :type course_tab: CourseTab
    :param assign_instructor_tab: The reference to the assign instructor tab.
    :type assign_instructor_tab: AssignInstructorTab
    :param enroll_students_tab: The reference to the enroll students tab.
    :type enroll_students_tab: EnrollStudentsTab
    """
    def __init__(self, notebook, student_tab, instructor_tab, course_tab, assign_instructor_tab, enroll_students_tab):
        self.load_store_tab = ttk.Frame(notebook)
        notebook.add(self.load_store_tab, text="Manage Data")
        
        self.student_tab = student_tab
        self.instructors_tab = instructor_tab
        self.courses_tab = course_tab
        self.assign_instructor_tab = assign_instructor_tab
        self.enroll_students_tab = enroll_students_tab

        form_frame = tk.Frame(self.load_store_tab)
        form_frame.grid(row=1, column=0, rowspan=6, padx=10, pady=10, sticky="n")

        load_button = tk.Button(self.load_store_tab, text="Load JSON Data", command=self.load_all_data)
        load_button.grid(row=2, column=0, padx=5, pady=5)

        save_button = tk.Button(self.load_store_tab, text="Save Data as JSON", command=self.save_all_data)
        save_button.grid(row=3, column=0, padx=5, pady=5)
        
        save_csv_button = tk.Button(self.load_store_tab, text="Save Data as CSV", command=self.save_all_data_as_csv)
        save_csv_button.grid(row=4, column=0, padx=5, pady=5)

        backup_button = tk.Button(self.load_store_tab, text="Backup Database", command=self.backup_database)
        backup_button.grid(row=5, column=0, padx=5, pady=5)

    def save_all_data(self):
        """
        Save all data (students, instructors, and courses) to a JSON file.

        Prompts the user to select a directory and saves the data in JSON format. Displays a success or error message based on the result.
        """
        directory = filedialog.askdirectory(
            title="Select Directory to Save JSON File"
        )
        if not directory:
            return

        filepath = os.path.join(directory, 'extracted_data.json')
        try:
            data = {
                'students': [student.serialize() for student in self.student_tab.students],
                'instructors': [instructor.serialize() for instructor in self.instructors_tab.instructors],
                'courses': [course.serialize() for course in self.courses_tab.courses]
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo("Success", "Data saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving data: {str(e)}")

    def save_all_data_as_csv(self):
        """
        Save all data (students, instructors, and courses) to CSV files.

        Prompts the user to select a directory and saves the data in separate CSV files (students.csv, instructors.csv, courses.csv). Displays a success or error message based on the result.
        """
        directory = filedialog.askdirectory(
            title="Select Directory to Save CSV Files"
        )
        if not directory:
            return

        try:
            students_file = os.path.join(directory, 'students.csv')
            with open(students_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Name', 'Age', 'Email', 'Student ID', 'Registered Courses'])
                for student in self.student_tab.students:
                    registered_courses = '; '.join([course.course_id for course in student.registered_courses])
                    writer.writerow([student.name, student.age, student.get_email(), student.student_id, registered_courses])

            instructors_file = os.path.join(directory, 'instructors.csv')
            with open(instructors_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Name', 'Age', 'Email', 'Instructor ID', 'Assigned Courses'])
                for instructor in self.instructors_tab.instructors:
                    assigned_courses = '; '.join([course.course_id for course in instructor.assigned_courses])
                    writer.writerow([instructor.name, instructor.age, instructor.get_email(), instructor.instructor_id, assigned_courses])

            courses_file = os.path.join(directory, 'courses.csv')
            with open(courses_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Course ID', 'Course Name', 'Instructor ID', 'Enrolled Students'])
                for course in self.courses_tab.courses:
                    instructor_id = course.instructor.instructor_id if course.instructor else ''
                    enrolled_students = '; '.join([student.student_id for student in course.enrolled_students])
                    writer.writerow([course.course_id, course.course_name, instructor_id, enrolled_students])

            messagebox.showinfo("Success", f"Data saved as CSV files in '{directory}'.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving CSV data: {str(e)}")

    def load_all_data(self):
        """
        Load data (students, instructors, and courses) from a JSON file.

        Prompts the user to select a JSON file and loads the data into the application. The data is validated and any inconsistencies are auto-corrected. Displays success, warning, or error messages based on the result.
        """
        try:
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                title="Select Data File",
                filetypes=(("JSON Files", "*.json"), ("All Files", "*.*"))
            )
            if not filename:
                return

            with open(filename, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", f"No data file found at '{filename}'.")
            return
        except json.JSONDecodeError as e:
            messagebox.showerror("Error", f"Error decoding JSON: {str(e)}")
            return
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred while reading the file: {str(e)}")
            return

        try:
            if not all(key in data for key in ('students', 'instructors', 'courses')):
                messagebox.showerror("Error", "Data file is missing required sections.")
                return

            courses = {}
            instructors = {}
            students = {}

            email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")

            for course_data in data['courses']:
                try:
                    if not isinstance(course_data['course_id'], str) or not course_data['course_id']:
                        raise ValueError("Invalid course ID.")
                    if not isinstance(course_data['course_name'], str) or not course_data['course_name']:
                        raise ValueError("Invalid course name.")

                    course = Course(course_data['course_id'], course_data['course_name'], None, [])
                    courses[course.course_id] = course
                except KeyError as e:
                    messagebox.showerror("Error", f"Missing key in course data: {str(e)}")
                    return
                except ValueError as ve:
                    messagebox.showerror("Error", f"Invalid data in course: {ve}")
                    return

            for instructor_data in data['instructors']:
                try:
                    if not isinstance(instructor_data['name'], str) or not instructor_data['name']:
                        raise ValueError("Invalid instructor name.")
                    if not isinstance(instructor_data['instructor_id'], str) or not instructor_data['instructor_id']:
                        raise ValueError("Invalid instructor ID.")
                    if not isinstance(instructor_data['age'], int):
                        raise ValueError("Instructor age must be an integer.")
                    if not email_pattern.match(instructor_data['email']):
                        raise ValueError("Invalid instructor email address.")

                    instructor = Instructor(
                        instructor_data['name'],
                        instructor_data['age'],
                        instructor_data['email'],
                        instructor_data['instructor_id'],
                        []
                    )
                    instructors[instructor.instructor_id] = instructor
                except KeyError as e:
                    messagebox.showerror("Error", f"Missing key in instructor data: {str(e)}")
                    return
                except ValueError as ve:
                    messagebox.showerror("Error", f"Invalid data in instructor: {ve}")
                    return

            for student_data in data['students']:
                try:
                    if not isinstance(student_data['name'], str) or not student_data['name']:
                        raise ValueError("Invalid student name.")
                    if not isinstance(student_data['student_id'], str) or not student_data['student_id']:
                        raise ValueError("Invalid student ID.")
                    if not isinstance(student_data['age'], int):
                        raise ValueError("Student age must be an integer.")
                    if not email_pattern.match(student_data['email']):
                        raise ValueError("Invalid student email address.")

                    student = Student(
                        student_data['name'],
                        student_data['age'],
                        student_data['email'],
                        student_data['student_id'],
                        []
                    )
                    students[student.student_id] = student
                except KeyError as e:
                    messagebox.showerror("Error", f"Missing key in student data: {str(e)}")
                    return
                except ValueError as ve:
                    messagebox.showerror("Error", f"Invalid data in student: {ve}")
                    return

            for course_data in data['courses']:
                course = courses[course_data['course_id']]
                instructor_id = course_data.get('instructor_id')
                if instructor_id:
                    if instructor_id in instructors:
                        course.instructor = instructors[instructor_id]
                    else:
                        messagebox.showwarning("Warning", f"Instructor ID '{instructor_id}' for course '{course.course_name}' not found.")
                enrolled_student_ids = course_data.get('enrolled_students', [])
                course.enrolled_students = []
                for s_id in enrolled_student_ids:
                    if s_id in students:
                        course.enrolled_students.append(students[s_id])
                    else:
                        messagebox.showwarning("Warning", f"Student ID '{s_id}' enrolled in course '{course.course_name}' not found.")

            for instructor_data in data['instructors']:
                instructor = instructors[instructor_data['instructor_id']]
                assigned_course_ids = instructor_data.get('assigned_courses', [])
                instructor.assigned_courses = []
                for c_id in assigned_course_ids:
                    if c_id in courses:
                        instructor.assigned_courses.append(courses[c_id])
                    else:
                        messagebox.showwarning("Warning", f"Course ID '{c_id}' assigned to instructor '{instructor.name}' not found.")

            for student_data in data['students']:
                student = students[student_data['student_id']]
                registered_course_ids = student_data.get('registered_courses', [])
                student.registered_courses = []
                for c_id in registered_course_ids:
                    if c_id in courses:
                        student.registered_courses.append(courses[c_id])
                    else:
                        messagebox.showwarning("Warning", f"Course ID '{c_id}' registered by student '{student.name}' not found.")

            inconsistencies_found = False

            for student in students.values():
                for course in student.registered_courses:
                    if student not in course.enrolled_students:
                        course.enrolled_students.append(student)
                        inconsistencies_found = True
                        messagebox.showwarning("Warning", f"Student '{student.name}' registered for course '{course.course_name}' but was not enrolled. Auto-corrected.")

            for course in courses.values():
                for student in course.enrolled_students:
                    if course not in student.registered_courses:
                        student.registered_courses.append(course)
                        inconsistencies_found = True
                        messagebox.showwarning("Warning", f"Student '{student.name}' enrolled in course '{course.course_name}' but had not registered. Auto-corrected.")

            for course in courses.values():
                instructor = course.instructor
                if instructor:
                    if course not in instructor.assigned_courses:
                        instructor.assigned_courses.append(course)
                        inconsistencies_found = True
                        messagebox.showwarning("Warning", f"Course '{course.course_name}' is assigned to instructor '{instructor.name}' but was not in the instructor's assigned courses. Auto-corrected.")

            for instructor in instructors.values():
                for course in instructor.assigned_courses:
                    if course.instructor != instructor:
                        course.instructor = instructor
                        inconsistencies_found = True
                        messagebox.showwarning("Warning", f"Instructor '{instructor.name}' has course '{course.course_name}' in assigned courses but was not set as the course's instructor. Auto-corrected.")

            if inconsistencies_found:
                messagebox.showinfo("Notice", "Inconsistencies found in data were auto-corrected. Please review your data.")

            clear_db = db.clear_all_tables()
            if(not(clear_db)):
                messagebox.showerror("Error", f"An error occurred while clearing the tables")
                return 
            for course in courses.values():
                course.save_to_db()
            
            for student in students.values():
                student.save_to_db()
            
            for instructor in instructors.values():
                instructor.save_to_db()
            
            for student in students.values():
                student.handle_course_enrollment()
                        
            for instructor in instructors.values():
                instructor.handle_course_assignment()

            self.student_tab.students = list(students.values())
            self.instructors_tab.instructors = list(instructors.values())
            self.courses_tab.courses = list(courses.values())

            self.student_tab.update_student_treeview()
            self.instructors_tab.update_instructor_treeview()
            self.courses_tab.update_course_treeview()

            self.enroll_students_tab.update_students()
            self.enroll_students_tab.update_courses()
            self.assign_instructor_tab.update_instructors()
            self.assign_instructor_tab.update_courses()

            messagebox.showinfo("Success", "Data loaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading data: {str(e)}")

    def backup_database(self):
        """
        Backup the current SQLite database.

        Prompts the user to select a location to save the backup and creates a backup of the database in the specified location. Displays a success or error message based on the result.
        """
        try:
            backup_file = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
            )
            
            if not backup_file:
                return
            
            with closing(db.connection.cursor()) as cursor:
                with sqlite3.connect(backup_file) as backup_conn:
                    db.connection.backup(backup_conn)
                    
            messagebox.showinfo("Success", f"Database backup successful!\nBackup saved as: {backup_file}")
        
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during backup: {str(e)}")