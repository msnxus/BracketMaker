import os
import sys
import psycopg2
import dotenv

dotenv.load_dotenv()
DATABASE_URL = os.environ['DATABASE_URL']


def main():
    try:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT name FROM bracket")
                table = cursor.fetchall()
                for row in table:
                    print(row)
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)
        
if __name__ == '__main__':
    main()