#!/usr/bin/env python

#-----------------------------------------------------------------------
# bracket.py
# Authors: Billy Cohen and Stefan Gjaja
#-----------------------------------------------------------------------

import sys
import contextlib
import sqlite3
import flask
# import registrar_helper as hlpr

#-----------------------------------------------------------------------

app = flask.Flask(__name__, template_folder='.')
DATABASE_URL = 'file:reg.sqlite?mode=ro'

#-----------------------------------------------------------------------

# default path, displays the results of course query
@app.route('/', methods=['GET'])

# # path when there are input fields into one of the four boxes
@app.route('/?', methods=['GET'])

# loads basic page with course results from query
def index():
    html_code = flask.render_template('index.html')
    response = flask.make_response(html_code)
    return response

# displays when url is regdetails, course specific page
@app.route('/createbracket', methods=['GET'])

def create_bracket():
    html_code = flask.render_template('createbracket.html')
    response = flask.make_response(html_code)
    return response

@app.route('/viewbracket', methods=['GET'])

def view_bracket():
    # Take in query
    code = flask.request.args.get('code')
    if code is None:
        code = ''

    html_code = flask.render_template('viewbracket.html', code=code)
    response = flask.make_response(html_code)
    return response

@app.route('/viewbracket/', methods=['GET'])

def view_bracket_code():
    html_code = flask.render_template('test.html')
    response = flask.make_response(html_code)
    return response



    # # Take in query
    # dept = flask.request.args.get('dept')
    # if dept is None:
    #     dept = ''
    # coursenum = flask.request.args.get('coursenum')
    # if coursenum is None:
    #     coursenum = ''
    # area = flask.request.args.get('area')
    # if area is None:
    #     area = ''
    # title = flask.request.args.get('title')
    # if title is None:
    #     title = ''

    # html_code = flask.render_template('index.html',
    #     dept=dept, coursenum=coursenum, area=area, title=title)

    # # Create table with dept, coursenum, area, and title
    # try:
    #     html_code += hlpr.add_table_info(dept, coursenum, area, title)
    # except Exception as ex:
    #     print(str(sys.argv[0]) + ": " + str(ex), file=sys.stderr)
    #     html_code = flask.render_template(
    #                     'error.html',
    #                     message = 'A server error occurred. ' +
    #                     'Please contact the system administrator.')
    #     response = flask.make_response(html_code)
    #     return response

    # html_code += flask.render_template('footer.html')

    # # Use cookies to eventually do second class search from details page
    # response = flask.make_response(html_code)
    # response.set_cookie('dept', dept)
    # response.set_cookie('coursenum', coursenum)
    # response.set_cookie('area', area)
    # response.set_cookie('title', title)
    # return response

#-----------------------------------------------------------------------

# # Error handler for class_id, returns true and the class_id, if found,
# # or returns false and the error message
# def __classid_error_helper__():
#     class_id = flask.request.args.get('classid')
#     if class_id is None or class_id == '':
#         html_code = flask.render_template(
#              'error.html', message = 'missing classid')
#         response = flask.make_response(html_code)
#         return (False, response)

#     try:
#         class_id = int(class_id)
#         class_id = str(class_id)

#     except Exception as ex:
#         ex = 'non-integer classid'
#         html_code = flask.render_template(
#             'error.html', message = ex)
#         response = flask.make_response(html_code)
#         return (False, response)

#     return (True, class_id)

# # displays when url is regdetails, course specific page
# @app.route('/regdetails', methods=['GET'])

# # displays course information
# def query_results():
#     try:
#         with sqlite3.connect(DATABASE_URL, isolation_level=None,
#         uri=True) as connection:

#             with contextlib.closing(connection.cursor()) as cursor:

#                 # Get classid
#                 # MODULARIZE
#                 class_id = __classid_error_helper__()
#                 if not class_id[0]:
#                     return class_id[1]

#                 class_id = class_id[1]
#                 # Save previous search
#                 dept = flask.request.cookies.get('dept')
#                 coursenum = flask.request.cookies.get('coursenum')
#                 area = flask.request.cookies.get('area')
#                 title = flask.request.cookies.get('title')

#                 # Get class details
#                 classdetails = ''
#                 try:
#                     classdetails = hlpr.create_details(class_id, cursor)

#                 except ValueError as ex:
#                     html_code = flask.render_template('error.html',
#                                                        message = ex)
#                     response = flask.make_response(html_code)
#                     return response

#                 except Exception as ex:
#                     print(str(sys.argv[0]) + ": " + str(ex),
#                           file=sys.stderr)
#                     html_code = flask.render_template(
#                         'error.html',
#                         message = 'A server error occurred. ' +
#                         'Please contact the system administrator.')
#                     response = flask.make_response(html_code)
#                     return response

#                 html_code = flask.render_template('classdetails.html',
#                     classid = class_id, classdetails=classdetails)

#                 # Get class_id
#                 course_id = classdetails[0]
#                 html_code += hlpr.course_details_header(course_id)

#                 cross_listings = ''
#                 course_details = ''
#                 professors = ''

#                 try:
#                     # use course_id to get cross_listings
#                     cross_listings = hlpr.create_cross_listings(
#                     course_id, cursor)

#                     # use course_id to get course_details
#                     course_details =hlpr.create_class_info(
#                         course_id, cursor)

#                     # use course_id to get professors
#                     professors = hlpr.create_prof_info(
#                         course_id, cursor)

#                 except Exception as ex:
#                     print(str(sys.argv[0]) + ": " + str(ex),
#                           file=sys.stderr)
#                     html_code = flask.render_template(
#                         'error.html',
#                         message = 'A server error occurred. ' +
#                         'Please contact the system administrator.')
#                     response = flask.make_response(html_code)
#                     return response

#                 # use cross_listings, course_details, professors to get
#                 # the info for the course details table
#                 html_code += hlpr.add_course_details_table(
#                     cross_listings, course_details, professors)

#                 # Use cookies to do another class search
#                 html_code += hlpr.another_class_search(
#                     dept, coursenum, area, title)

#                 # Add footer
#                 html_code += flask.render_template('footer.html')

#                 response = flask.make_response(html_code)
#                 return response


    # except Exception as ex:
    #     print(str(sys.argv[0]) + ": " + str(ex), file=sys.stderr)
    #     sys.exit(1)
