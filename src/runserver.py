#! usr/bin/env python

#-----------------------------------------------------------------------
# runserver.py
# Authors: BracketMaker Team
#-----------------------------------------------------------------------

import sys
import argparse
import bracket

#-----------------------------------------------------------------------

DATABASE_URL = 'file:reg.sqlite?mode=ro'

# private method responsible for parsing user input and printing help
# menu exits with status 2 if there's an error
def __parse__():
    parser = argparse.ArgumentParser(
        description='Server for the registrar application')
    parser.add_argument('port', type=int,
                        help=
                        'the port at which the server should listen')
    return parser.parse_args()

def main():
    port = __parse__().port

    try:
        bracket.app.run(host = '0.0.0.0', port = port, debug = True)
    except Exception as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
