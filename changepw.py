import sqlite3

from werkzeug.security import generate_password_hash


db = sqlite3.connect("inventory.db")

def main():
    # Get email from user

    email = input("email: ")

    # Select user type
    role = input("role (admin or student): ")

    """ Check that the email exists in the correct database """
    if role == "student":
        cursor = db.execute("SELECT * FROM students WHERE email = ?", (email,))

    elif role == "admin":
        cursor = db.execute("SELECT * FROM admins WHERE email = ?", (email,))
    
    else:
        db.close()
        return print("Role not recognized")

    check_email = cursor.fetchone()
    cursor.close()

    if not check_email[0]:
        return print("Username not found in database")

    # If the username is in the database, hash it and update the table
    new_password = input("New password: ")
    hash_newpassword = generate_password_hash(new_password)
    
    if role == "student":
        db.execute("UPDATE students SET hash_password = ? WHERE email = ?", (hash_newpassword, email,))
    elif role == "admin":
        db.execute("UPDATE admins SET hash_password = ? WHERE email = ?", (hash_newpassword, email,))
    else:
        return print("Error")
        
    db.commit()
    db.close()

    print("Password changed successfully")

main()