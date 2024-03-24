import os
import sys
import psycopg2

DATABASE_URL = "dbname='bracket' user='nn3965' host='localhost' password='4234'"

def get_bracket_from_code(code):
    stmt_str = "SELECT names, game_title FROM bracket WHERE code = %s"
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute(stmt_str, (code,))
                row = cursor.fetchone()
                if row:
                    names, game_title = row
                    print(f"Names: {names}, Game Title: {game_title}")
                else:
                    print("No bracket found with the given code.")
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
        
