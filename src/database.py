import os
import sys
import psycopg2
from datetime import datetime, timedelta

# You will need to set up 
DATABASE_URL = "dbname='bracket' user='bracket_maker' host='localhost' password='cos333'"

def initialize():

    stmt_str = "DROP TABLE IF EXISTS bracket;"
    stmt_str_syslog = "DROP TABLE IF EXISTS system_log;"
    stmt_str_users = "DROP TABLE IF EXISTS users;"

    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute(stmt_str)
                cursor.execute(stmt_str_syslog)
                cursor.execute(stmt_str_users)
                connection.commit()
                print("Previous Table Deleted")
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

    stmt_str = "CREATE TABLE bracket (code CHAR(4) PRIMARY KEY, ser_bracket JSONB, owner TEXT)"
    stmt_str_syslog = 'CREATE TABLE system_log (id SERIAL PRIMARY KEY,type VARCHAR(255),time TIMESTAMP WITHOUT TIME ZONE,netid VARCHAR(255) NULL,description TEXT NULL)'
    stmt_str_users = 'CREATE TABLE users (netid VARCHAR PRIMARY KEY,email VARCHAR,phone VARCHAR);'

    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute(stmt_str)
                cursor.execute(stmt_str_syslog)
                cursor.execute(stmt_str_users)
                connection.commit()
                print("Tables Created")
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

def create_bracket(code, ser_bracket, netid):
    stmt_str = "INSERT INTO bracket (code, ser_bracket, owner) VALUES (%s, %s, %s)"
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute(stmt_str, (code, ser_bracket, netid))
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

# Adds a system log into the database
def add_system_log(type, netid=None, description=''):
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                time = datetime.now()
                stmt_str = "INSERT INTO system_log (type, time, netid, description) VALUES (%s, %s, %s, %s)"
                cursor.execute(stmt_str, (type, time, netid, description))
                connection.commit()
                print("syslog logged an event")
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

# Checks if netid exists in users table
def is_user_created(netid):
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT netid FROM users WHERE netid = %s", (netid.rstrip(),))
                    return cursor.fetchone() is not None
    except psycopg2.Error as e:
        print(e, file=sys.stderr)
        return False

# Creates user if it doesn't already exist
def create_user(netid):
    if is_user_created(netid):
        print(f'user {netid} already exists', file=sys.stderr)
        return
    netid_cleaned = netid.rstrip()
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
                with connection.cursor() as cursor:
                    # Insert into users table
                    cursor.execute(
                        "INSERT INTO users (netid, email, phone) VALUES (%s, %s, '')",
                        (netid_cleaned, f'{netid_cleaned}@princeton.edu'))
                    
                    connection.commit()  # Commit the transaction
                    print(f'successfully created user {netid_cleaned}')
    except psycopg2.Error as e:
        print(e, file=sys.stderr)
        connection.rollback()  # Rollback the transaction on error