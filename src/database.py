import os
import sys
import psycopg2
from datetime import datetime, timedelta

# You will need to set up 

# DATABASE_URL = "dbname='bracket' user='bracket_maker' host='localhost' password='cos333'"
DATABASE_URL = "dbname='bracket' user='nn3965' host='localhost' password='4234'"
# DATABASE_URL = "dbname='bracket' user='postgres' host='localhost' password='cos333'"
# DATABASE_URL = "dbname='bracket' user='postgres' host='localhost' password='Majorcheck112233!'"
# DATABASE_URL = 'postgres://bracket_sa3u_user:zIWzQ9iIrc21F0EVdRTheCpNZ23nX6Fi@dpg-cobap5779t8c73br7rig-a/bracket_sa3u'


def initialize():

    stmt_str = "DROP TABLE IF EXISTS bracket;"
    stmt_str_syslog = "DROP TABLE IF EXISTS system_log;"
    stmt_str_users = "DROP TABLE IF EXISTS users;"
    stmt_str_players = "DROP TABLE IF EXISTS players;"


    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute(stmt_str)
                cursor.execute(stmt_str_syslog)
                cursor.execute(stmt_str_users)
                cursor.execute(stmt_str_players)
                connection.commit()
                print("Previous Table Deleted")
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

    stmt_str = "CREATE TABLE bracket (code CHAR(4) PRIMARY KEY, name TEXT, num_players INT, time TIMESTAMP WITHOUT TIME ZONE, ser_bracket JSONB, owner TEXT);"
    stmt_str_syslog = 'CREATE TABLE system_log (id SERIAL PRIMARY KEY,type VARCHAR(255),time TIMESTAMP WITHOUT TIME ZONE,netid VARCHAR(255) NULL,description TEXT NULL);'
    stmt_str_users = 'CREATE TABLE users (netid VARCHAR PRIMARY KEY,email VARCHAR,phone VARCHAR);'
    stmt_str_players = 'CREATE TABLE players (code CHAR(4), netid VARCHAR(255), PRIMARY KEY (code, netid));'

    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute(stmt_str)
                cursor.execute(stmt_str_syslog)
                cursor.execute(stmt_str_users)
                cursor.execute(stmt_str_players)
                connection.commit()
                print("Tables Created")
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
    

def create_bracket(code, name, num_players, ser_bracket, netid):
    if get_bracket_from_code(code) != False:
        print("A bracket with code", code, "already exists. Please create a new code.")
        return True
    time = datetime.now()
    stmt_str = "INSERT INTO bracket (code, name, num_players, time, ser_bracket, owner) VALUES (%s, %s, %s, %s, %s, %s)"
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute(stmt_str, (code, name, num_players, time, ser_bracket, netid))
                connection.commit()
                print("New Bracket Successfully Created")
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
    return False
        
# Return the bracket corresponding to the code
def get_bracket_from_code(code):
    stmt_str = "SELECT ser_bracket FROM bracket WHERE code = %s"
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute(stmt_str, (str(code),))
                row = cursor.fetchone()
                if row:
                    # print("Bracket:", row)
                    return row
                else:
                    print("No bracket found with the given code.")
                    return False
                
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

def get_potential_brackets(code, name, owner):
    values = []
    code = str(code)
    code = "%" + code
    code = code + "%"
    values.append(code)
    stmt_str = "SELECT code, name, num_players, owner FROM bracket WHERE code LIKE %s ESCAPE '/'"

    #Add on any qualifiers
    if name is not None:
        stmt_str += " AND name LIKE %s ESCAPE '/'"
        name = str(name)
        name = "%" + name
        name = name + "%"
        values.append(name)

    if owner is not None:
        stmt_str += " AND owner LIKE %s ESCAPE '/'"
        owner = str(owner)
        owner = "%" + owner
        owner = owner + "%"
        values.append(owner)


    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute(stmt_str, values)
                table = cursor.fetchall()
                if table:
                    # print("Bracket:", row)
                    return table
                else:
                    print("No bracket found with the given code.")
                    print(code)
                    print(str(code))
                    return None
                
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

# add all provided players to the players table assoc with the given code
def store_players_with_code(code, players):
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
                with connection.cursor() as cursor:
                    # Insert into users table
                    for player in players:
                        if player != 'guest':
                            cursor.execute(
                                "INSERT INTO players (code, netid) VALUES (%s, %s)",
                                (code, player))
                            connection.commit()  # Commit the transaction
    except psycopg2.Error as e:
        print(e, file=sys.stderr)
        connection.rollback()  # Rollback the transaction on error
        
def update_bracket(code, bracket):
    stmt_str = "UPDATE bracket SET ser_bracket = %s WHERE code = %s "
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute(stmt_str, (bracket, code))
                connection.commit()
                print("Updated Bracket")
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

# Returns all the info for brackets a player is a part of
def get_participating_brackets(netid):
    print("NETID: " + str(netid))
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                stmt_str = "SELECT code FROM players WHERE netid = %s"
                cursor.execute(stmt_str, (netid,))
                connection.commit()
                participating_bracket_codes = cursor.fetchall()
                ret = []

                print("CODES: " + str(participating_bracket_codes))
                for code in participating_bracket_codes:
                    stmt_str = "SELECT * FROM bracket WHERE code = %s"
                    cursor.execute(stmt_str, (code,))
                    connection.commit()
                    ret.append(cursor.fetchone()) # Should only be one result
                return ret
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

# Returns all the owned brackets in a list
def get_owned_brackets(netid):
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                time = datetime.now()
                stmt_str = "SELECT * FROM bracket WHERE owner = %s"
                cursor.execute(stmt_str, (netid,))
                connection.commit()
                return cursor.fetchall()
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

def is_owner(code, netid):
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT owner FROM bracket WHERE code = %s", (code,))
                    id = cursor.fetchone()
                    if id != None:
                        if id[0] == netid: return True
                    return False
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