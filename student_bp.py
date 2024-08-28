from flask import Blueprint, Flask, flash, redirect, render_template, request, session
from flask_session import Session
import sqlite3

from db_helpers import confirm_query_exists, extract_query_info
from helpers import login_required

# Configure the blueprint
bp = Blueprint('student', __name__)

# Global Variables
db_name = "inventory"

# Chem 2A / 2B Bin Items
bin_contents = {
    "wash_bottle": "Wash Bottle", 
    "grad_cyl_10": "10-mL Graduated Cylinder", 
    "grad_cyl_50": "50-mL Graduated Cylinder",
    "stir_rod": "Stir Rod",
    "short_fun":"Short Funnel",
    "long_fun":"Long Funnel",
    "beaker_400":"400-mL Beaker (x2)",
    "beaker_250": "250-mL Beaker (x2)",
    "beaker_150": "150-mL Beaker",
    "beaker_50": "50-mL Beaker",
    "watch_glass": "Watch Glass",
    "plastic_pipets": "Plastic Pipets",
    "balance": "Balance"
    } 

statusses = ["clean",
          "dirty",
          "partial",
          "missing"]

@bp.route("/assign", methods = ["GET", "POST"])
@login_required
def assign():
    
    # This page will have the student be updated in the class roster and have their bin number assigned
    if request.method == "POST":  

        # Make sure that student has included all of the form input values
        semester = request.form.get("semester")
        crn = request.form.get("crn")
        room_num = request.form.get("room_num")
        bin_num = request.form.get("bin_num")
        confirmation = request.form.get("confirmation")
        student_id = session["user_id"]

        if not semester or not crn:
            flash("Please fill in the semester and/or crn information")
            return render_template("assign.html")
        
        if not room_num or not bin_num or not confirmation:
            flash(f"Please fill in the room and bin number, {room_num}, {bin_num}")
            return render_template("assign.html")

        # The query table for class assignment will be classes
        table1 = "classes"

        # Check that the class code is there
        class_query = {
            "crn": f"{crn}", 
            "semester": f"{semester}"
        }

        if not confirm_query_exists(db_name, table1, class_query):
            flash("Class does not exist...ask instructor to register the class")
            return render_template("assign.html")

        # Extract class code
        class_code = extract_query_info(db_name, table1, class_query, "class_code")

        if not class_code:
            flash("Database error, class code not found")
            return render_template("assign.html")

        # Extract bin code
        table2 = "bins"
        bin_query = {
            "room_num": f"{room_num}",
            "bin_num": f"{bin_num}"
        } 
        bin_code = extract_query_info(db_name, table2, bin_query, "bin_code")
        
        if not bin_code:
            flash("Bin does not exist or bin has not yet been registered in room")
            return render_template("assign.html")
        

        # Check that the bin number chosen has not yet been selected by someone in the class
        table3 = "bin_assign"
        assign_query = {
            "class_code": f"{class_code}",
            "bin_code": f"{bin_code}"
        }

        if confirm_query_exists(db_name, table3, assign_query):
            flash(f"Sorry, you or someone else in your class has already been assigned to that bin (bin# {bin_num})")
            return render_template("assign.html")

        # Update the bin_assign db with the student id and bin code assigned
        # !!!! You may have to find another error for the except block !!!
        try:
            with sqlite3.connect(f"{db_name}.db") as db:
                db.execute("INSERT INTO bin_assign (class_code, student_id, bin_code) VALUES (?, ?, ?)", (class_code, student_id, bin_code))
        except sqlite3.Error as e:
            flash(f"An error occurred, {e}")
            return render_template("assign.html")

        # Confirm that the info is in the database and then assign the student bin and the current class info
        # This will save the student's CURRENT bin_code and class_code (this may change if user has to register again in a diff. semester or class)
        if confirm_query_exists(db_name, table3, assign_query):
            flash("Registration successful!")
            session["student_bin"] = bin_code
            session["class_code"] = class_code
            return redirect("/status")
        else:
            flash("Registration failed - not found in db")
            return render_template("assign.html")
        
    else:
        
        # Remind user to only submit if they have yet been assigned a bin
        user_id = session["user_id"]

        # Check to see if user has previously registered a bin
        student_query = {"student_id": f"{user_id}"}
        assigned_class = confirm_query_exists(db_name, "bin_assign", student_query)

        if assigned_class:
            assigned_bin_code = extract_query_info(db_name, "bin_assign", student_query, "bin_code")

            num_query = {"bin_code" : f"{assigned_bin_code}"}
            assigned_bin_num = extract_query_info(db_name, "bins", num_query, "bin_num" )

            flash(f"Reminder: You have already previously registered for a bin (Bin Number {assigned_bin_num} ). Only fill in this form if you need to register a new bin for a new class. Ask your instructor if you need to be reassigned to a new bin")

        return render_template("assign.html") 


@bp.route("/status", methods = ["GET", "POST"])
@login_required
def status():
    # This should provide the current status of student's assigned bin
    # Should include status of every item that's supposed be in the bin and also overall status
    # Should also provide a flagged message if previous student gave a flagged comment

    student_id = session["user_id"]

    # Make sure the user has been assigned to a class
    id_query = {"student_id" : f"{student_id}"}
    class_code = extract_query_info(db_name, "bin_assign", id_query, "class_code")

    if not class_code:
        flash("No class found or class not assigned")
        return redirect("/assign")
    
    # Make sure student has been assigned to a bin for the current class
    class_student_query = {"class_code" : f"{class_code}", "student_id" : f"{student_id}"}
    bin_code = extract_query_info(db_name, "bin_assign", class_student_query, "bin_code")
    
    if not bin_code:
        flash("You have not yet registered in a class or to a bin")
        return redirect("assign.html")

    # Generate status of items in assigned bin, save to a dictionary

    # Turn the bin_contents list into a sql search query
    sql_col_search = ', '.join(f"bin_items.{items}" for items in bin_contents)

    with sqlite3.connect(f"{db_name}.db") as db:
        try:
             db.row_factory = sqlite3.Row
             cursor = db.execute(f"SELECT bins.bin_num, {sql_col_search} FROM bin_items JOIN bins ON bins.bin_code = bin_items.bin_code WHERE bin_items.bin_code = ?", (bin_code,))
             bin_status = cursor.fetchone()
             cursor.close()

        except sqlite3.Error as e:
            flash(f"An error has occurred, {e}")
            return redirect("/")
        
    if not bin_status:
        flash("Database error, bin_status not found")
        return redirect("/")
          
    return render_template("status.html", bin_status=bin_status, bin_contents=bin_contents)


@bp.route("/checkin", methods = ["GET", "POST"])
@login_required
def bin_check_in():
    # This is the place where students should give status of items in bin
    # Should include status of every item that's supposed be in the bin and also overall status
    # Include space to provide a flagged comment to previous student
    
    # First get the user's information
    student_id = session["user_id"]

    # If assigned, get bin_code from student's id
    id_query = {"student_id" : f"{student_id}"}
    bin_code = extract_query_info(db_name, "bin_assign", id_query, "bin_code")

    if not bin_code:
        flash("You have not yet been assigned to a bin")
        return redirect("/assign.html")
    
    if request.method == "POST":
        
        # This will create a dict that has all of the form submissions user changed
        update_item_status = {}
        for item in bin_contents:
            status = request.form.get(f"{item}")
            if status in statusses:
                update_item_status[f"{item}"] = status

        # Create sql query that updates the info for bin_num
        col_query = ", ".join(f"{key} = ?" for key in update_item_status)
        values = list(update_item_status.values())
        values.append(student_id)
        values.append(bin_code)

        # Update the bin_items table with the reported statusses
        with sqlite3.connect(f"{db_name}.db") as db:
            try:
                db.execute(f"UPDATE bin_items SET {col_query}, "\
                       "last_user_code = ?,"\
                       "last_checkin_time = datetime('now')"
                       "WHERE bin_code = ?", (values))
                db.commit()
            except sqlite3.Error as e:
                flash(f"Database update error updated, {e}")
                return render_template("checkin.html", statusses=statusses, bin_contents=bin_contents)

        # Let user know the update was successful
        flash ("Check-in Successful!")
        return redirect("/success")
        
    return render_template("checkin.html", statusses=statusses, bin_contents=bin_contents)


@bp.route("/checkout", methods = ["GET", "POST"])
@login_required
def bin_check_out():
    # This is the place where students should give status of items in bin at check out
    
    # Check to see if student has already registered a bin

    # First get the student's bin information
    student_id = session["user_id"]

    # If assigned, get bin_code from student's id
    id_query = {"student_id" : f"{student_id}"}
    bin_code = extract_query_info(db_name, "bin_assign", id_query, "bin_code")

    if not bin_code:
        flash("You have not yet been assigned to a bin")
        return redirect("/assign.html")
    
    if request.method == "POST":
            
        # This will create a dict that has all of the form submissions user changed
        update_item_status = {}
        for item in bin_contents:
            status = request.form.get(f"{item}")
            if status in statusses:
                update_item_status[f"{item}"] = status

        # Create sql query that updates the info for bin_num
        col_query = ", ".join(f"{key} = ?" for key in update_item_status)
        values = list(update_item_status.values())
        values.append(student_id)
        values.append(bin_code)

        # Update the bin_items table
        with sqlite3.connect(f"{db_name}.db") as db:
            try:
                db.execute(f"UPDATE bin_items SET {col_query}, "\
                    "last_user_code = ?, "\
                    "last_checkout_time = datetime('now')"
                    "WHERE bin_code = ?", (values))
                db.commit()
            except sqlite3.Error as e:
                flash(f"Database update error, {e}")
                return render_template("checkout.html", statusses=statusses, bin_contents=bin_contents)

            # Let user know the update was successful
            flash ("Check-Out Successful!")
            return redirect("/")
                
    return render_template("checkout.html", statusses=statusses, bin_contents=bin_contents)