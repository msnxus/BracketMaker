import os
import sys
import psycopg2
from create_bracket import create_bracket

DATABASE_URL = "dbname='bracket' user='nn3965' host='localhost' password='4234'"

def main():
    create_bracket(1234, "Super Smash Bros", ["Nico", "Billy", "Ryan"])
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM bracket")
                table = cursor.fetchall()
                for row in table:
                    print(row)
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
        
if __name__ == '__main__':
    main()