import os
import sys
import psycopg2

DATABASE_URL = "dbname='bracket' user='nn3965' host='localhost' password='4234'"

def create_bracket(code, game_title, names):
    stmt_str = "INSERT INTO bracket (code, game_title, names) VALUES (%s, %s, %s)"
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute(stmt_str, (code, game_title, names))
                connection.commit()
                print("New Bracket Successfully Created")
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
        
