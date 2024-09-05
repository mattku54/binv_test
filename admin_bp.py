from flask import Blueprint, Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from datetime import datetime

import sqlite3
import json

from student_bp import bin_contents, statusses

from helpers import admin_login_required
from db_helpers import confirm_query_exists, extract_query_info

# Configure blueprint
bp = Blueprint('admin', __name__)

# Global variables
db_name = "inventory"

@bp.route("/class_status", methods = ["GET", "POST"])
@admin_login_required
def class_bin_status():
    # This should provide a table that lists all of the assigned bins + students for instructor's class with an overall status
    # Should also indicate if there are any flagged messages for students

    if request.method == "POST":

        # Let the user select the semester and crn
        semester = request.form.get("semester")
        crn = request.form.get("crn")

        if not semester or not crn:
            flash("Please input the semester and crn")
            return render_template("class_status.html")

        # Find the class_code of the class the teacher specified
        class_query = {"semester" : f"{semester.upper()}", "crn" : f"{crn}" } 
        table = "classes"
        class_code = extract_query_info(db_name, table, class_query, "class_code")

        if not class_code:
            flash("Class not found")
            return render_template("class_status.html")
        
        # Generate a list of tuples of all of the bin_num, the statusses and the student assigned
        with sqlite3.connect(f"{db_name}.db") as db:
            try:
                db.row_factory = sqlite3.Row
                cursor = db.execute("SELECT bins.bin_num, students.FirstName, students.LastName, bin_items.* "\
                "FROM bin_assign "\
                "JOIN students ON students.pcc_id = bin_assign.student_id "\
                "JOIN bins ON bins.bin_code = bin_assign.bin_code "\
                "JOIN bin_items ON bins.bin_code = bin_items.bin_code "\
                "WHERE bin_assign.class_code = ? "\
                "ORDER BY bins.bin_num", class_code)

                bin_statusses = cursor.fetchall()
                cursor.close()

            except sqlite3.Error as e:
                print(f"Database error, {e}")
                flash(f"Database error, {e}")
                return render_template("class_status.html")  
            
        return render_template("class_status.html", bin_statusses=bin_statusses, bin_contents=bin_contents, semester=semester, crn=crn)
    
    else:
        return render_template("class_status.html")
        

@bp.route("/register_class", methods = ["GET", "POST"])
@admin_login_required
def class_register():
    # This should register a class...admins only
        # If user has submitted registration info
    if request.method == "POST":
        # User input parameters
        class_name = request.form.get("class")
        crn = request.form.get("crn")
        semester = request.form.get('semester')
        room_num = request.form.get('room_num')
        instructor_id = session["user_id"]

        # For queries, we're going to select from the "classes" table
        table = "classes"

        # Check that the user filled in every spot on the form
        if not crn or not semester or not room_num:
            flash("Please fill in every spot on the form")
            return render_template("register_class.html")


        # Query the db to see if class has already registered or email is being used        
        class_query = {"crn": f"{crn}", "semester": f"{semester}"}

        if confirm_query_exists(db_name, table, class_query):
            flash("Class already exists")
            return render_template("register_class.html")
        
        # Add the class to the table
        with sqlite3.connect(f"{db_name}.db") as db:
            try:
                db.execute("INSERT INTO classes (instructor_id, crn, semester, room_num, class_name) VALUES (?, ?,?,?,?)", (instructor_id, crn, semester.upper(), room_num.upper(), class_name.upper()))
            except sqlite3.Error as e:
                flash(f"Database error, {e}")
                return render_template("register_class.html")
        
        # Confirm that it worked
        if confirm_query_exists(db_name, table, class_query):
            flash("Registration successful!")
            return redirect("/")
        else:
            flash("Registration Unsuccessful...you may have already registered or the email address is already in use")
            return render_template("register_class.html")

    # If method is "GET" or user is still logging in
    else:
        return render_template("register_class.html")

@bp.route("/register_bins", methods = ["GET", "POST"])
@admin_login_required
def register_bins():
    # This should register all of the bins in a room
    if request.method == "POST":
        # User input parameters
        room_num = request.form.get('room_num')
        bin_count = request.form.get('bin_count')

        # Check that the user filled in every spot on the form
        if not room_num or not bin_count:
            flash("Please fill in every spot on the form")
            return render_template("register_bins.html")
        
        try:
            bin_count_num = int(bin_count)
        except ValueError as e:
            flash(f"Put in positive integer number of bins, {e}")
            return render_template("register_bins.html")
            
        
        # Make sure user has put in a positive integer for bin_count
        if not bin_count.isdigit() or int(bin_count) < 0:
            flash("Please input an integer number of bins")
            return render_template("register_bins.html")

        room_query = {"room_num": f"{room_num}"}
        # Query the db to see if the room is already in the rooms table
        if not confirm_query_exists(db_name, "rooms", room_query):      
            # If the room is not in the rooms table, add it
            with sqlite3.connect(f"{db_name}.db") as db:
                try:
                    db.execute("INSERT INTO rooms (room_num) VALUES (?)", (room_num,))
                    db.commit()
                except sqlite3.Error as e:
                    flash("Database error", e)
                    return render_template("register_bins.html")

        
        # Query the db to see if bins have already been registered for that room      
        if confirm_query_exists(db_name, "bins", room_query):
            flash(f"Bins for {room_num} are already registered")
            return render_template("register_bins.html")
        
        # Generate bin numbers (1 to bin_count + 1) to a list...default starting from 1
        bin_num_list = []

        for i in range(bin_count_num):
            bin_num_list.append(str(i + 1))
        
        # Add the bins to the bins table...also add entries to the bin_items table
        with sqlite3.connect(f"{db_name}.db") as db:
            try:
                for i in range (bin_count_num):
                    db.execute("INSERT INTO bins (room_num, bin_num) VALUES (?,?)", (room_num.upper(), bin_num_list[i]))
                    db.execute("INSERT INTO bin_items (bin_code) VALUES (NULL)")
                db.commit()

            except sqlite3.Error as e:
                flash("Database error", e)
                return render_template("register_bins.html")
        
        # Confirm that it worked
        if confirm_query_exists(db_name, "bins", room_query):
            flash("Registration successful!")
            return render_template("register_bins.html")
        else:
            flash("Registration Unsuccessful. There was an error in the database")
            return render_template("register_bins.html")

    # If method is "GET" or user is still logging in
    return render_template("register_bins.html")

@bp.route("/edit_class", methods = ["GET", "POST"])
@admin_login_required
def edit_class():
    # This should give admins the ability to edit class rosters (including bin assignments) and update bin status
    # Update info: bin_items (status of items), bin_assign (change bin assignment for student), class_roster
    # Add info/class: class_roster (add student to class)

    if request.method == "POST":
        
        # Find the class
        semester = request.form.get("semester")
        crn = request.form.get("crn")

        if not semester or not crn:
            flash("Please input a semester or crn")
            return render_template("edit_class.html")

        class_query = {"semester" : f"{semester}", "crn" : f"{crn}"}
        class_code = extract_query_info(db_name, "classes", class_query, "class_code")
        if not class_code:
            flash("Class not found")
            return render_template("edit_class.html")
        
        room_num = extract_query_info(db_name, "classes", class_query, "room_num")

        # Code path to update bin assignment...put in info
        bin_num = request.form.get('empty_bins')

        if not bin_num:
            flash("Please select a new bin to be assigned")
            return render_template("edit_class.html")

        # Find the bin_code
        bin_query = {"bin_num": f"{bin_num}", "room_num": f"{room_num}"}
        bin_code = extract_query_info(db_name, "bins", bin_query, "bin_code")
        
        # Check to make sure that the bin has not yet been assigned in the class      
        assign_query = {"bin_code": f"{bin_code}", "class_code": f"{class_code}"}

        if confirm_query_exists(db_name, "bin_assign", assign_query):
            flash("Bin already assigned to another user...select another bin")
            return render_template("edit_class.html")
    

        # Check to make sure student is enrolled in the class
        student_id = request.form.get('students')

        if not student_id:
            flash(f"Please select a student, id = {student_id}")
            return render_template("edit_class.html")
        
        student_query = {"student_id" : student_id, "class_code" : class_code}
        if not confirm_query_exists (db_name, "bin_assign", student_query):
            flash(f"Error: User is not registered in this class, ID = {student_id}, class_code = {class_code}")
            return render_template("edit_class.html")

        # Update bin_assign with the new bin number for the student
        with sqlite3.connect(f"{db_name}.db") as db:
            try:
                db.execute("UPDATE bin_assign SET bin_code = ? "\
                           "WHERE student_id = ?"\
                           "AND class_code = ?", (bin_code, student_id, class_code,))
                db.commit()
            except sqlite3.Error as e:
                flash(f"Database error: {e}")
                return render_template("edit_class.html")
        
        # Confirm that it worked
        check_bin_code = extract_query_info(db_name, "bin_assign", student_query, "bin_code")

        if bin_code != check_bin_code:
            flash("Database error: Database did not update")
            return render_template("edit_class.html")
        else:
            flash("Bin assignment changed successfully!")
            return render_template("edit_class.html")

    return render_template("edit_class.html")

@bp.route("/student_empty_lists", methods = ["GET", "POST"])
@admin_login_required
def student_empty_lists():
    
    # Retrieve the data from the query parameters
    semester = request.args.get('semester')
    crn = request.args.get('crn')

    # Student-list will be a dict-like object with bin numbers and student info
    student_list = student_bin_list(semester, crn)

    # Empty_bins will be a set (list in js) with the empty bins for the class
    empty_bins = empty_bin_list(semester, crn)

    return jsonify({"student_list" : student_list, "empty_bins" : empty_bins})


def student_bin_list(semester, crn):
    # Generate a list of students enrolled in a class
    
    class_query = {"semester" : semester, "crn": crn}
    class_code = extract_query_info(db_name, "classes", class_query, "class_code")

    if not class_code:
        flash("Class not found")
        return

    # This should generate a dict-like object result that has the names and bin assignments for the class
    with sqlite3.connect(f"{db_name}.db") as db:
        try:
            db.row_factory = sqlite3.Row
            cursor = db.execute("SELECT bins.bin_num, students.FirstName, students.LastName, students.pcc_id FROM " \
                       "students JOIN bin_assign ON students.pcc_id = bin_assign.student_id " \
                       "JOIN bins on bins.bin_code = bin_assign.bin_code " \
                        "WHERE bin_assign.class_code = ? " \
                        "ORDER by bins.bin_num", (class_code,))
            student_list_rows = cursor.fetchall()
            cursor.close()

        except sqlite3.Error as e:
            flash(f"A server error has occured in student_bin_list: {e}")
            return
        
    student_list = [dict(row) for row in student_list_rows]
    
    return student_list

def empty_bin_list(semester, crn):

    class_query = {"semester" : semester, "crn": crn}
    class_code = extract_query_info(db_name, "classes", class_query, "class_code")
    
    if not class_code:
        flash("Class not found")
        return
    
    room_num = extract_query_info(db_name, "classes", class_query, "room_num")

    if not room_num:
        flash("Room not found")
        return

    # This should generate a dict-like object result that has all of the assigned bin numbers for a class
    # Use the same db connection to find the highest bin number for a room
    with sqlite3.connect(f"{db_name}.db") as db:
        try:
            cursor1 = db.execute("SELECT bins.bin_num FROM "\
                       "bins JOIN bin_assign ON bins.bin_code = bin_assign.bin_code " \
                        "WHERE bin_assign.class_code = ? "\
                        "ORDER by bins.bin_num", (class_code,))
            assigned_bin_nums = cursor1.fetchall()

            cursor2 = db.execute("SELECT bin_num FROM bins WHERE room_num = ? "\
                                  "ORDER BY bin_num DESC", (room_num,))
            result2 = cursor2.fetchone()

            try:
                highest_assigned_bin_num = int(result2[0])
            except ValueError as e:
                flash(f"Database error: {e}")
                return
                            
            cursor1.close()
            cursor2.close()

        except sqlite3.Error as e:
            flash(f"A server error has occured in empty_bin_list: {e}")
            return
        
    empty_bin_set= set(range(1, highest_assigned_bin_num +1 ))
    assigned_bin_set = set()
    for i in range (len(assigned_bin_nums)):
        assigned_bin_set.add(assigned_bin_nums[i][0])

    empty_bin_set = empty_bin_set - assigned_bin_set
    empty_bin_list = list(empty_bin_set)
    
    return empty_bin_list

@bp.route("/edit_bin_status", methods = ["GET", "POST"])
@admin_login_required
def edit_bin_status():
        # Info from user on which bin to update
        if request.method == "POST":
            room_num = request.form.get("room_num")
            bin_num = request.form.get("bin_num")

            # Confirm that the user put in the room number and bin number
            if not room_num or not bin_num:
                flash("Please input a room number and a bin number")
                return render_template("edit_bin_status.html",bin_contents=bin_contents, statusses=statusses)
            
            # Get the bin_code to update the status
            bin_code_query = {"room_num" : f"{room_num.upper()}", "bin_num" : f"{bin_num}"}
            bin_code = extract_query_info(db_name, "bins", bin_code_query, "bin_code")

            if not bin_code:
                flash("Bin does not exist")
                return render_template("edit_bin_status.html", bin_contents=bin_contents, statusses=statusses)

            # Create dict to store the form requests for the bin items that user actually input
            update_bin_items = {}
            for item in bin_contents:
                item_status = request.form.get(f"{item}")
                if item_status:
                    update_bin_items[item] = item_status

            # Create sql query based on the dict
            update_sql_query = ", ".join(f"{key} = ?" for key in update_bin_items)
            values = list(update_bin_items.values())
            values.append(bin_code)

            # Update the table
            with sqlite3.connect(f"{db_name}.db") as db:
                try:
                    db.execute(f"UPDATE bin_items "\
                            f"SET {update_sql_query} "\
                            "WHERE bin_code = ?", (values))
                    db.commit()
                except sqlite3.Error as e:
                    flash(f"Error when updating database, {e}, {update_sql_query}")
                    return render_template("edit_bin_status.html", bin_contents=bin_contents, statusses=statusses)
            
            flash("Update successful")
            return redirect("/class_status")
        
        return render_template("edit_bin_status.html", bin_contents=bin_contents, statusses=statusses)

@bp.route("/confirm_bin", methods = ["GET", "POST"])
@admin_login_required
def confirm_bin():
    
    # Retrieve the data from the query parameters
    room_num = request.args.get('room_num')
    bin_num = request.args.get('bin_num')

    # Attempt to extract a bin code
    bin_query = {"room_num" : f"{room_num.upper()}", "bin_num" : f"{bin_num}"} 
    bin_code = extract_query_info(db_name, "bins", bin_query, "bin_code")

    if not bin_code:
        flash("Bin not found.")
        return 'false'
    else:
        return bin_code