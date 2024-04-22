#!/usr/bin/env python

#-----------------------------------------------------------------------
# bracket.py
# Authors: Billy Cohen and Lucas Linzmeier
#-----------------------------------------------------------------------

import sys
import contextlib
import sqlite3
import flask
from flask import redirect, url_for, Flask, request, jsonify
import random


# -------------- COMMENT THESE OUT TO RUN LOCALLY --------------
# from src.bracket_logic import Bracket
# from src.database import get_bracket_from_code, update_bracket
# -------------- UNCOMMENT THESE TO RUN LOCALLY --------------
from bracket_logic import Bracket
from database import get_bracket_from_code, update_bracket

import random
import CASClient as CASClient
import database


#-----------------------------------------------------------------------
secret_key = 'RyansBigOlBalls'

app = flask.Flask(__name__, template_folder='templates')
app.secret_key = secret_key
# DATABASE_URL = 'file:reg.sqlite?mode=ro'
_cas = CASClient.CASClient()

# private method that redirects to landing page
# if user is not logged in with CAS
# or if user is logged in with CAS, but doesn't have entry in DB
def redirect_login():
    return not _cas.is_logged_in() or not database.is_user_created(_cas.authenticate())

#-----------------------------------------------------------------------

# default path, displays the results of course query
@app.route('/', methods=['GET'])

# # path when there are input fields into one of the four boxes
@app.route('/?', methods=['GET'])

# # path when there are input fields into one of the four boxes
@app.route('/index', methods=['GET'])
# loads basic page with course results from query
def index():
    if redirect_login():
        netid = None
    else:
        netid = _cas.authenticate()
        netid = netid.rstrip()
    html_code = flask.render_template('index.html', user=netid)
    response = flask.make_response(html_code)
    return response

@app.route('/logout', methods=['GET'])
def logout():
    _cas.logout()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET'])
def login():
    netid = _cas.authenticate()
    netid = netid.rstrip()

    database.add_system_log('user', netid, f'Login by user {netid}')

    if not database.is_user_created(netid):
        database.create_user(netid)

    return redirect(url_for('index'))

# displays when url is regdetails, course specific page
@app.route('/createbracket', methods=['GET'])
def create_bracket():
    if redirect_login():
        return redirect(url_for('login'))
    netid = _cas.authenticate()
    netid = netid.rstrip()
    # Take in query
    name = flask.request.args.get('name')
    if name is None:
        name = ''

    teams = flask.request.args.get('teams')
    if teams is None:
        teams = ''

    html_code = flask.render_template('createbracket.html', name=name, teams=teams)
    response = flask.make_response(html_code)
    return response

@app.route('/viewbracketpage/', methods=['GET'])
def temp_bracket():
    code = flask.request.args.get("code")
    if redirect_login():
        netid = None
    else:
        netid = _cas.authenticate()
        netid = netid.rstrip()
    if database.is_owner(code, netid):
        return redirect(url_for('view_bracket_with_code', code=code))
    
    players = []
    bracket = Bracket("", players)
    

    bracket.load(code)


    rounds = int(bracket.max_round()) + 1
    bracket_list = bracket.bracket_list()
    round_indicies = bracket.round_indicies()
    name = bracket.name

    html_code = flask.render_template('viewbracketpage.html',round_indicies=round_indicies, name=name, rounds=rounds, code=code,
                                      bracket_list=bracket_list)
    
    response = flask.make_response(html_code)
    return response
    

@app.route('/createbracket/addteams/', methods=['GET'])
def add_teams():
    if redirect_login():
        return redirect(url_for('login'))
    netid = _cas.authenticate()
    netid = netid.rstrip()

    name = flask.request.args.get('name')

    #Lucas - Potential non-integer could be passed - have to account for this
    teams = int(flask.request.args.get('teams'))


    html_code = flask.render_template('addteams.html',name=name, teams=teams)


    response = flask.make_response(html_code)

    #Lucas - There might be problems setting this as a cookie
    response.set_cookie("teams", str(teams))
    response.set_cookie("name", name)

    return response

@app.route('/createbracket/seeding_confirmation/', methods=['GET'])
def bracket_seeding_confirmation():
    if redirect_login():
        return redirect(url_for('login'))
    netid = _cas.authenticate()
    netid = netid.rstrip()

    code = __generate_code__()
    
    # get cookies
    team_names = []
    teams = int(flask.request.cookies.get("teams"))

    name = flask.request.cookies.get("name")


    for team in range(1, teams+1):
        team_names.append(flask.request.args.get("team%s" % (team)))
    team_set = set(team_names)
    duplicates = len(team_set) != len(team_names)
    if duplicates:
        error_message = "Please do not enter teams with duplicate names!"
        html_code = flask.render_template('addteams.html', code=code, teams = teams, error_message = error_message, team_names = team_names)
        response = flask.make_response(html_code)
        return response

    html_code = flask.render_template('bracketconfirmation.html', team_names=team_names, code=code, netid=netid)

    response = flask.make_response(html_code)

    # Lucas - Make the bracket object
    bracket = Bracket(name, team_names)


    ser_bracket = bracket.serialize()

    response.set_cookie("bracket", ser_bracket)
    # response.set_cookie("team_names", team_names)


    return response

@app.route('/createbracket/random_confirmation/', methods=['GET'])
def bracket_random_confirmation():
    if redirect_login():
        return redirect(url_for('login'))
    netid = _cas.authenticate()
    netid = netid.rstrip()

    code = __generate_code__()

    # get cookies
    team_names = []
    teams = int(flask.request.cookies.get("teams"))

    name = flask.request.cookies.get("name")


    for team in range(1, teams+1):
        team_names.append(flask.request.args.get("team%s" % (team)))
    team_set = set(team_names)
    duplicates = len(team_set) != len(team_names)
    if duplicates:
        error_message = "Please do not enter teams with duplicate names!"
        html_code = flask.render_template('addteams.html', code=code, teams = teams, error_message = error_message, team_names = team_names)
        response = flask.make_response(html_code)
        return response
    
    random.shuffle(team_names)
    html_code = flask.render_template('bracketconfirmation.html', team_names=team_names, code=code, netid=netid)

    response = flask.make_response(html_code)

    # Lucas - Make the bracket object
    bracket = Bracket(name, team_names)

    ser_bracket = bracket.serialize()

    response.set_cookie("bracket", ser_bracket)
    # response.set_cookie("team_names", team_names)


    return response

@app.route('/storebracket/', methods=['POST'])
def store_bracket():

    #Here we need to actually grab the bracket and put it in the database
    players = []
    bracket = Bracket("", players) # ADD TEAM NAME
    # try:
    bracket.deserialize(flask.request.cookies.get("bracket"))

    code = int(flask.request.form.get("code"))
    owner = str(flask.request.form.get("owner"))

    code_exists = bracket.store(code, owner)
    if code_exists:
        error_message =  'A bracket with this code already exists. Please create a new code.'
        team_names = []
        # team_names = (flask.request.cookies.get("team_names"))

        teams = int(flask.request.cookies.get("teams"))
        print("TEAMSSSSSSSSS", teams)
        name = flask.request.cookies.get("name")
        for team in range(1, teams+1):
            team_names.append(flask.request.args.get("team%s" % (team)))
        print("TEAMSSSSSSSSS", team_names)


        html_code = flask.render_template('bracketconfirmation.html', team_names=team_names, code=code, error_message=error_message)
        response = flask.make_response(html_code)
        bracket = Bracket(name, team_names)
        ser_bracket = bracket.serialize()

        response.set_cookie("bracket", ser_bracket)
        return response
        # html_code = flask.render_template(
        #                 'error.html',
        #                 message = 'A bracket with this code already exists. Please create a new code.')
        
        # MAKE THIS JUST APPEAR ON SCREEN, NOT MAKE A NEW SCREEN, ADD BUTTON
        response = flask.make_response(html_code)
        return response

    # return redirect(url_for('run_bracket', code=code))
    # return redirect(url_for('view_created_bracket', code=code))

    return redirect(url_for('view_bracket_with_code', code=code))

 # FROM CREATE BRACKET
@app.route('/editbracket/', methods=['GET'])
def view_bracket_with_code():
    code = flask.request.args.get("code")

    if redirect_login():
        netid = None
    else:
        netid = _cas.authenticate()
        netid = netid.rstrip()
    if not database.is_owner(code, netid):
        return redirect(url_for('temp_bracket', code=code))
    
    players = []
    bracket = Bracket("", players)
    code_exists = get_bracket_from_code(code)
    if not code_exists:
        error_message =  'A bracket with this code does not exist. Please enter a valid code.'

        html_code = flask.render_template('entercode.html', code=code, error_message = error_message)
        response = flask.make_response(html_code)
        return response


    #NEXT: ENTERING A CODE TO A BRACKET THAT DOESN'T APPEAR CAUSES ERROR

    bracket.load(code)

    rounds = int(bracket.max_round()) + 1
    bracket_list = bracket.bracket_list()
    round_indicies = bracket.round_indicies()
    name = bracket.name

    html_code = flask.render_template('editbracket.html',round_indicies=round_indicies, name=name, rounds=rounds, code=code,
                                      bracket_list=bracket_list)
    
    response = flask.make_response(html_code)
    return response

@app.route('/editbracket/', methods = ['POST'])
def update_scores():
    code = flask.request.args.get('code')
    data = get_bracket_from_code(code)
    bracket = data[0][1]
    
    # Update player scores
    players = []
    my_bracket = Bracket("", players)
    my_bracket.load(code)
    for i in range(1, len(bracket)-1):
        if bracket[i] is not None:
            round = my_bracket.get_round(i-1)
            player_name = bracket[i][0]
            player_value = flask.request.form.get(str(i))
            if player_value == None:
                player_value = 0
            my_bracket.update_score(player_name, round, player_value)
    print("using this bracket to set winners:", my_bracket.to_string())
    my_bracket.set_winners()
    update_bracket(code, my_bracket.serialize())
    return flask.redirect(f"/editbracket/?code={code}")

# FROM HOME PAGE, WHEN CODE IS NOT PROVIDED.
@app.route('/entercode/', methods=['GET'])
def view_bracket():
    # Take in query
    code = flask.request.args.get('code')
    if code is None:
        code = ''
    error_message = 'None'
    code_exists = get_bracket_from_code(code)
    if code == '':
        html_code = flask.render_template('entercode.html', code=code, error_message = error_message)
        response = flask.make_response(html_code)
        return response
    
    if code_exists == False and code != '':
        error_message = 'A bracket with this code does not exist. Please enter a valid code.'

        html_code = flask.render_template('entercode.html', code=code, error_message = error_message)
        response = flask.make_response(html_code)
        return response
    
    return redirect(url_for('temp_bracket', code=code))

def __generate_code__():
    # generate random 4 digit code
    code = '{:04}'.format(random.randint(0,9999))
    if not get_bracket_from_code(code):
        return code
    else:
        __generate_code__()

# Takes in the bracket Code and outputs the name of the bracket
def __code_to_name__(code):

    # insert code
    return "Smash Bros"

