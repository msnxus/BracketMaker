import os
import sys
import psycopg2
from create_bracket import create_bracket
from get_bracket_from_code import get_bracket_from_code

DATABASE_URL = "dbname='bracket' user='nn3965' host='localhost' password='4234'"

def test_create_bracket():
    create_bracket(1234, "Super Smash Bros", ["Nico", "Billy", "Ryan"])

def fetch_all_info():
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
        
def test_get_bracket():
    get_bracket_from_code(1234)

def main():
    # test_create_bracket()
    # fetch_all_info()
    test_get_bracket()
    
        
if __name__ == '__main__':
    main()