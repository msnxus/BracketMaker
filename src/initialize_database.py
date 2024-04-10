# Initializes the database !!!! Will clear all existing data
#-----------------------------------------------------------------------
# -------------- COMMENT THIS OUT TO RUN LOCALLY --------------
# import src.database
# -------------- UNCOMMENT THIS TO RUN LOCALLY --------------
import database

def main():
    database.initialize()

#-----------------------------------------------------------------------
if __name__ == '__main__':
    main()