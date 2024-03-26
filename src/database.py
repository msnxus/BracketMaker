import os
import sys
import psycopg2

# You will need to set up 
DATABASE_URL = "dbname='bracket' user='bracket_maker' host='localhost' password='cos333'"

def initialize():

    stmt_str = "DROP TABLE IF EXISTS bracket;"

    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute(stmt_str)
                connection.commit()
                print("Previous Table Deleted")
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

    stmt_str = "CREATE TABLE bracket (code CHAR(4) PRIMARY KEY, ser_bracket JSONB)"

    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute(stmt_str)
                connection.commit()
                print("New Table Created")
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
    

def create_bracket(code, ser_bracket):
    stmt_str = "INSERT INTO bracket (code, ser_bracket) VALUES (%s, %s)"
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute(stmt_str, (code, ser_bracket))
                connection.commit()
                print("New Bracket Successfully Created")
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
        
def get_bracket_from_code(code):
    stmt_str = "SELECT ser_bracket FROM bracket WHERE code = %s"
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute(stmt_str, (code,))
                row = cursor.fetchone()
                if row:
                    return row
                else:
                    print("No bracket found with the given code.")
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)