#!/usr/bin/env python

#-----------------------------------------------------------------------
# bracket.py
# Authors: Billy Cohen and Lucas Linzmeier
#-----------------------------------------------------------------------

import sys
import contextlib
import sqlite3
import flask
from flask import redirect, url_for
from bracket_logic import Bracket

from database import get_bracket_from_code, update_bracket

import random


#-----------------------------------------------------------------------

app = flask.Flask(__name__, template_folder='templates')
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

@app.route('/createbracket/addteams/', methods=['GET'])
def add_teams():
    name = flask.request.args.get('name')

    #Lucas - Potential non-integer could be passed - have to account for this
    teams = int(flask.request.args.get('teams'))


    html_code = flask.render_template('addteams.html',name=name, teams=teams)


    response = flask.make_response(html_code)

    #Lucas - There might be problems setting this as a cookie
    response.set_cookie("teams", str(teams))
    response.set_cookie("name", name)

    return response

@app.route('/createbracket/confirmation/', methods=['GET'])
def bracket_confirmation():
    code = __generate_code__()
    
    # get cookies
    team_names = []
    teams = int(flask.request.cookies.get("teams"))

    name = flask.request.cookies.get("name")


    for team in range(1, teams+1):
        team_names.append(flask.request.args.get("team%s" % (team)))

    html_code = flask.render_template('bracketconfirmation.html', team_names=team_names, code=code)

    response = flask.make_response(html_code)

    # Lucas - Make the bracket object
    bracket = Bracket(name, team_names)


    ser_bracket = bracket.serialize()

    response.set_cookie("bracket", ser_bracket)

    return response

@app.route('/storebracket/', methods=['POST'])
def store_bracket():
    #Here we need to actually grab the bracket and put it in the database
    players = []
    bracket = Bracket("", players)
    bracket.deserialize(flask.request.cookies.get("bracket"))

    code = flask.request.form.get("code")

    #Lucas - Put the bracket to the database
    bracket.store(code)

    return redirect(url_for('run_bracket', code=code))

@app.route('/createdbracket/', methods=['GET'])
def run_bracket():
    players = []
    bracket = Bracket("", players)

    code = flask.request.args.get("code")
    bracket.load(code)

    rounds = str(int(bracket.max_round()) + 1)
    grid_friendly_names = bracket.grid_friendly_players()
    name = bracket.name

    # Would need to check if this code exists
    html_code = flask.render_template('runbracketviewable.html',team_names=grid_friendly_names, name=name, rounds=rounds)
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
    code = flask.request.args.get('code')
    data = get_bracket_from_code(code)
    title= data[0][0]
    bracket = data[0][1]
            
    # Would need to check if this code exists
    html_code = flask.render_template('viewspecificbracket.html',title = title, code=code, bracket = bracket)
    response = flask.make_response(html_code)
    return response
        
@app.route('/viewbracket/', methods=['POST'])
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
            my_bracket.update_score(player_name, round, player_value)
    print("using this bracket to set winners:", my_bracket.to_string())
    my_bracket.set_winners()
    update_bracket(code, my_bracket.serialize())
    
    return flask.redirect(f"/viewbracket/?code={code}")

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

