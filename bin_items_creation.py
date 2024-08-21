import sqlite3
from db_helpers import confirm_query_exists

db_name = "inventory"

# Chem 2A / 2B Bin Contents

class_titles = ["CHEM 2A", 
                "CHEM 1A", 
                "CHEM 2B", 
                "CHEM 22"]

bin_contents = [
    "wash_bottle", 
    "grad_cyl_10", 
    "grad_cyl_50",
    "stir_rod",
    "short_fun",
    "long_fun",
    "beaker_400",
    "beaker_250",
    "beaker_150",
    "beaker_50",
    "watch_glass",
    "plastic_pipets",
    "balance"] 

statusses = ["clean",
          "dirty",
          "partial",
          "missing"]

room_num = ["SV20",
        "SV22",
        "SV18",
        "SV17",
        "SV21"]



def main():
    create_table_rows()
    return
    
def create_table():
    # This will create the "bin_items" table in the db
    # Take the table name
    table_name = input("Table Name? ")

    status_list = ', '.join(f"'{s}'" for s in statusses)

    column_creation = ', '.join(f"{item} TEXT CHECK({item} IN ({status_list}))" for item in bin_contents)

    sql_query = f"CREATE TABLE {table_name} ("\
    "bin_code INTEGER NOT NULL PRIMARY KEY, "\
    f"{column_creation}, "\
    "last_user_code INTEGER, "\
    "last_checkin_time DATETIME DEFAULT CURRENT_TIMESTAMP, "\
    "last_checkout_time DATETIME DEFAULT CURRENT_TIMESTAMP, "\
    "FOREIGN KEY (last_user_code) REFERENCES students (student_id), "\
    "FOREIGN KEY (bin_code) REFERENCES bins (bin_code)"\
    ");"\

    print(f"{sql_query}")

    with sqlite3.connect("inventory.db")as db:
        try:
            db.execute(f"{sql_query}")
            db.commit()

        except sqlite3.Error as e:
            print(f"Database error, {e} ")

    table_name_query = {"name" : f"{table_name}"}
    if confirm_query_exists(db_name, "sqlite_master", table_name_query):
        print(f"{table_name} in {db_name}.db successfully created")
        return
    else:
        print("Table not created")

def create_table_rows():
    table_name = input("Table Name? ")
    num_of_rows = input("Number of rows? ")
    num_start = input("Starting number? ")
    
    try:
        count_num = int(num_of_rows)
        start_num = int(num_start)
    except ValueError as e:
        print(f"Put in positive integer number of bins, {e}")
        return
    
    num_list = []

    for i in range(count_num):
        num_list.append(str(i+start_num))
    
    with sqlite3.connect(f"{db_name}.db") as db:
        try:
            for i in range(count_num):
                db.execute(f"INSERT INTO {table_name} (bin_code) VALUES (?)", (num_list[i],))
            db.commit()
        except sqlite3.Error as e:
            print(f"Database error, {e}")
            return
    return
    
main()