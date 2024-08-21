import sqlite3
from datetime import datetime, timedelta
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session


# This first function is only useful if there are many columns that you want to check the values of
def create_query_dict(column_names, values):
    return dict(zip(column_names, values))


def confirm_query_exists(db_name, table, queries_dict):
    # Connect to the db and check a table to see if a query value exists
    # with statement executes the content_expression and handles cleanup
    # queries_dict will be a dict of the table column and the query for that column
    try:
        with sqlite3.connect(f"{db_name}.db") as db:
            
            # Construct where clause (join combines the and statements and ? is there for parameter sub)
            where_conditions = ' AND '.join(f"{query_col} = ?" for query_col in queries_dict.keys())
            sql_query = f"SELECT * FROM {table} WHERE {where_conditions}"

            # Gather query values
            query_values = list(queries_dict.values())

            # Execute the search using the constructed where clause and paramters
            cursor = db.execute(sql_query, query_values)
            check = cursor.fetchall()

            cursor.close()

            if len(check) > 0:
                return True
            else:
                return False

    except sqlite3.Error as e:
        print(f"An error occurred confirming {query_values} exist in {table}: {e}")
        return False
    
def extract_query_info(db_name, table, queries_dict, value_search):
        
    try:
        # Connect to the db and extract a piece of information
        # with statement executes the content_expression and handles cleanup
        # queries_dict will be a dict of the table column and the query for that column
        with sqlite3.connect(f"{db_name}.db") as db:
            
            # Construct where clause (join combines the and statements and ? is there for parameter sub)
            where_conditions = ' AND '.join(f"{query_col} = ?" for query_col in queries_dict.keys())
            sql_query = f"SELECT {value_search} FROM {table} WHERE {where_conditions}"

            # Gather query values
            query_values = tuple(queries_dict.values())

            # Execute the search using the constructed where clause and parameters
            cursor = db.execute(sql_query, query_values)
            check = cursor.fetchall()
            cursor.close()

            if len(check) > 0:
                result = check[0][0]
                return str(result)
            
            else:
                return False
            
    except sqlite3.Error as e:
        print(f"An error occurred extracting {value_search} from {table}: {e}")   
        return False