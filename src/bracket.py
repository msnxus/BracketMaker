#!/usr/bin/env python

#-----------------------------------------------------------------------
# bracket.py
# Authors: Billy Cohen and Lucas Linzmeier
#-----------------------------------------------------------------------

import sys
import contextlib
import sqlite3
import json
import ast
import flask
from flask import redirect, url_for, Flask, request, jsonify
import random


# -------------- COMMENT THESE OUT TO RUN LOCALLY --------------
# from src.bracket_logic import Bracket
# from src.database import get_bracket_from_code, update_bracket
# -------------- UNCOMMENT THESE TO RUN LOCALLY --------------
from bracket_logic import Bracket
from database import get_bracket_from_code, update_bracket, get_potential_brackets

import random
import CASClient as CASClient
import database


#-----------------------------------------------------------------------
secret_key = 'sauce'

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

@app.context_processor
def utility_processor():
    return dict(zip=zip)

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

    num_teams = flask.request.args.get('num_teams')
    print(num_teams)
    if num_teams is None:
        num_teams = ''


    html_code = flask.render_template('createbracket.html', name=name, num_teams=num_teams)
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
    
    num_teams = flask.request.args.get('num_teams')

    name = flask.request.args.get('name')
    if name == '':
        error_message =  'Please enter a name for this bracket.'
        html_code = flask.render_template('createbracket.html', name=name, num_teams=num_teams, error_message=error_message)


    else:
        # Lucas - Potential non-integer could be passed - have to account for this
        # Billy is handling it
        try: 
            num_teams = int(flask.request.args.get('num_teams'))

            #Handling 0 or 1 teams
            if num_teams <= 1:
                error_message =  'You need at least 2 teams in your bracket!'
                html_code = flask.render_template('createbracket.html', name=name, num_teams=num_teams, error_message=error_message)

            elif num_teams > 1024:
                error_message =  'The maximum number of teams is 1024.'
                html_code = flask.render_template('createbracket.html', name=name, num_teams=num_teams, error_message=error_message)


            else:
                html_code = flask.render_template('addteams.html',name=name, num_teams=num_teams)

        except: 
            error_message =  'Please enter an integer value for number of teams.'
            html_code = flask.render_template('createbracket.html', name=name, num_teams=num_teams, error_message=error_message)




    response = flask.make_response(html_code)

    #Lucas - There might be problems setting this as a cookie
    response.set_cookie("num_teams", str(num_teams))
    response.set_cookie("name", name)
    # response.set_cookie("team_names", str(team_names))

    return response

@app.route('/createbracket/seeding_confirmation/', methods=['GET'])
def bracket_seeding_confirmation():
    if redirect_login():
        return redirect(url_for('login'))
    netid = _cas.authenticate()
    netid = netid.rstrip()

    code = __generate_code__()
    team_names = []

    # get cookies
    num_teams = int(flask.request.cookies.get("num_teams"))

    name = flask.request.cookies.get("name")

    player_names = []

    for team in range(1, num_teams+1):
        team_names.append(flask.request.args.get("team%s" % (team)))
        player_name = (flask.request.args.get("player%s" % (team)))
        if not database.is_user_created(player_name):
            player_names.append('guest')
        else: player_names.append(player_name)

    team_set = set(team_names)
    team_duplicates = len(team_set) != len(team_names)

    player_set = set(player_names)
    count_guest = sum(1 for item in player_names if item == "guest")
    netid_duplicates = len(player_set) != (len(player_names) - count_guest + 1)


    
    if '' in team_names:
        error_message = "Please enter a name for each team."
        html_code = flask.render_template('addteams.html', code=code, num_teams = num_teams, error_message = error_message, team_names = team_names, name = name)
        response = flask.make_response(html_code)
        return response
    
    if team_duplicates:
        error_message = "Two or more teams have the same name. Please do not enter teams with duplicate names."
        html_code = flask.render_template('addteams.html', code=code, num_teams = num_teams, error_message = error_message, team_names = team_names, name = name)
        response = flask.make_response(html_code)
        return response
    
    if netid_duplicates:
        error_message = "Two or more teams have the same netID. Please do not enter teams with duplicate netIDs."
        html_code = flask.render_template('addteams.html', code=code, num_teams = num_teams, error_message = error_message, team_names = team_names, name = name)
        response = flask.make_response(html_code)
        return response

    html_code = flask.render_template('bracketconfirmation.html', team_names=team_names, code=code, netid=netid, num_teams=num_teams, name=name, player_names=player_names)

    response = flask.make_response(html_code)

    # Lucas - Make the bracket object
    bracket = Bracket(name, team_names)


    ser_bracket = bracket.serialize()

    response.set_cookie("bracket", ser_bracket)
    response.set_cookie("team_names", str(team_names))
    response.set_cookie("num_teams", str(num_teams))
    response.set_cookie("player_names", str(player_names))
    response.set_cookie("mode", "seeded")

    print("Confirm TEAMSSSSSSSSS", team_names)

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
    num_teams = int(flask.request.cookies.get("num_teams"))

    name = flask.request.cookies.get("name")

    player_names = []

    for team in range(1, num_teams+1):
        team_names.append(flask.request.args.get("team%s" % (team)))
        player_name = (flask.request.args.get("player%s" % (team)))
        if not database.is_user_created(player_name):
            player_names.append('guest')
        else: player_names.append(player_name)
        
    team_set = set(team_names)
    team_duplicates = len(team_set) != len(team_names)

    player_set = set(player_names)
    count_guest = sum(1 for item in player_names if item == "guest")
    netid_duplicates = len(player_set) != (len(player_names) - count_guest + 1)    
    
    if '' in team_names:
        error_message = "Please enter a name for each team."
        html_code = flask.render_template('addteams.html', code=code, num_teams = num_teams, error_message = error_message, team_names = team_names, name = name)
        response = flask.make_response(html_code)
        return response
    
    if team_duplicates:
        error_message = "Two or more teams have the same name. Please do not enter teams with duplicate names."
        html_code = flask.render_template('addteams.html', code=code, num_teams = num_teams, error_message = error_message, team_names = team_names, name = name)
        response = flask.make_response(html_code)
        return response
    
    if netid_duplicates:
        error_message = "Two or more teams have the same netID. Please do not enter teams with duplicate netIDs."
        html_code = flask.render_template('addteams.html', code=code, num_teams = num_teams, error_message = error_message, team_names = team_names, name = name)
        response = flask.make_response(html_code)
        return response

    
    random.shuffle(team_names)
    html_code = flask.render_template('bracketconfirmation.html', team_names=team_names, code=code, netid=netid, num_teams=num_teams, name=name, player_names=player_names)

    response = flask.make_response(html_code)

    # Lucas - Make the bracket object
    bracket = Bracket(name, team_names)

    ser_bracket = bracket.serialize()

    response.set_cookie("bracket", ser_bracket)
    response.set_cookie("team_names", str(team_names))
    response.set_cookie("num_teams", str(num_teams))
    response.set_cookie("player_names", str(player_names))
    response.set_cookie("netid", netid)
    response.set_cookie("mode", "random")


    return response

@app.route('/storebracket/', methods=['POST'])
def store_bracket():
    if redirect_login():
        return redirect(url_for('login'))
    netid = _cas.authenticate()
    netid = netid.rstrip()


    #Here we need to actually grab the bracket and put it in the database
    players = []
    bracket = Bracket("", players) # ADD TEAM NAME
    # try:
    bracket.deserialize(flask.request.cookies.get("bracket"))

    code = flask.request.form.get("code")
    owner = str(flask.request.form.get("owner"))
    name = str(flask.request.form.get("name"))
    num_teams = int(flask.request.form.get("num_teams"))

    #LUCAS - IN CASE OF ERROR
    team_names = flask.request.cookies.get("team_names")
    team_names = ast.literal_eval(team_names)
    team_names = [str(x) for x in team_names] 

    netid = flask.request.cookies.get("netid")
    player_names = flask.request.cookies.get("player_names")
    player_names = ast.literal_eval(player_names)
    player_names = [str(x) for x in player_names] 


    #We need to ensure the code is a 4 digit number or else display an error message
    try:
        code = int(code)
    except:
        error_message =  'Please ensure the code is a 4 digit number.'

        html_code = flask.render_template('bracketconfirmation.html', 
            team_names=team_names, code=code, netid=netid, num_teams=num_teams, 
            name=name, player_names=player_names, error_message=error_message)
        response = flask.make_response(html_code)
        return response
    
    if(len(str(code)) != 4):
        error_message =  'Please ensure the code is a 4 digit number.'

        html_code = flask.render_template('bracketconfirmation.html', 
            team_names=team_names, code=code, netid=netid, num_teams=num_teams, 
            name=name, player_names=player_names, error_message=error_message)
        response = flask.make_response(html_code)
        return response


    code_exists = bracket.store(code, name, num_teams, owner)
    # team_names = []
    # team_names = (flask.request.cookies.getlist("team_names"))
    team_names = (flask.request.cookies.get("team_names"))
    print("please", team_names)
    team_names = ast.literal_eval(team_names)
    # print("please2", team_names)

    name = flask.request.cookies.get("name")

    player_names = (flask.request.cookies.get("player_names"))
    player_names = ast.literal_eval(player_names)



    if code_exists:
        error_message =  'A bracket with this code already exists. Please create a new code.'
        print("pretty please", team_names)
        html_code = flask.render_template('bracketconfirmation.html', num_teams = num_teams, team_names=team_names, code=code, error_message=error_message, name=name, netid=netid, player_names=player_names)
        response = flask.make_response(html_code)
        bracket = Bracket(name, team_names)
        ser_bracket = bracket.serialize()

        response.set_cookie("bracket", ser_bracket)
        return response
        # html_code = flask.render_template(
        #                 'error.html',
        #                 message = 'A bracket with this code already exists. Please create a new code.')
        
        # MAKE THIS JUST APPEAR ON SCREEN, NOT MAKE A NEW SCREEN, ADD BUTTON
        # response = flask.make_response(html_code)
        # return response

    # return redirect(url_for('run_bracket', code=code))
    # return redirect(url_for('view_created_bracket', code=code))

    players = flask.request.form.getlist('players')
    database.store_players_with_code(code, players)


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

# Profile page for user profiles
@app.route('/profile', methods=['GET'])
def profile():
    if redirect_login():
        return redirect(url_for('login'))
    
    netid = _cas.authenticate()
    user = netid.rstrip()

    hb = database.get_owned_brackets(user)
    pb = database.get_participating_brackets(user)

    html_code = flask.render_template('profile.html', user=user, hosted_brackets=hb, participating_brackets=pb)
    response = flask.make_response(html_code)
    return response

@app.route('/coderesults')
def get_results():
    #Get input
    code = flask.request.args.get("code")
    name = flask.request.args.get("name")
    owner = flask.request.args.get("owner")

    print(code)

    table = get_potential_brackets(code, name, owner)

    if table is None:
        html_code = flask.render_template("no_results.html")
        response = flask.make_response(html_code)
        return response
    
    #Make html code and response
    html_code = flask.render_template("results.html", table=table)
    response = flask.make_response(html_code)
    return response

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

