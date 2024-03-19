#! usr/bin/env python

#-----------------------------------------------------------------------
# bracket_logic.py
# Authors: BracketMaker Team
#-----------------------------------------------------------------------

import math

# ASK SAM
import sys
import os

# Add the parent directory to the Python path
utilsdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils'))
sys.path.append(utilsdir)

# from utils import utils

#-----------------------------------------------------------------------
# WILL PUT BACK INTO UTILS AFTER
def closest_power_of_two(num):
    power_of_two = 1
    while power_of_two < num:
        power_of_two *= 2
    return power_of_two

#-----------------------------------------------------------------------

class Bracket():

    # Given a list of players, make the initial bracket
    def __init__(self, players):
        self._bracket_list = []
        self.init_bracket(players)
        return
  
    def init_bracket(self, players):
        teams = len(players)
        bracket_size = closest_power_of_two(teams)
        self._bracket_list.append(teams)
        for player in players:
            self._bracket_list.append([player, 0])
        # Append None for the winners of all games
        for i in range(bracket_size-1):
            self._bracket_list.append(None)

    # Given player and round return index in underlying bracketlist
    # If nonreal round or nonexistent player return None
    def player_index_by_round(self, player, round):
        if round > self.max_round() or round < 0: return None # nonreal round

        initial_index = 0
        for i in range(self.num_players()):
            if self._bracket_list[i+1][0] == player:
                initial_index = i+1
                break
        
        if initial_index == 0: return None # nonreal player

        rank_in_round = math.ceil(initial_index / (2**round))

        return int(self.first_index_of_round(round) + rank_in_round - 1)
    
    # Return first index of round on range [0, total rounds]
    def first_index_of_round(self, round):
        if round > self.max_round() or round < 0: return None # nonreal round

        index = 1
        for i in range(round):
            index += closest_power_of_two(self.num_players()) / (2**i)
        return int(index)

    # Return number of players in bracket
    def num_players(self):
        return self._bracket_list[0]
    
    # Return list of all player names
    def players(self):
        players = []
        for i in range(self.num_players()):
            players.append(self._bracket_list[i+1][0]) # tuple, only return name
        return players
    
    # Return max round
    def max_round(self):
        return math.log(closest_power_of_two(self.num_players()), 2)

    # Update functions
    def update_score(self, player, round, score):
        if round >= self.max_round() or round < 0: return None # invalid round

        index = self.player_index_by_round(player, round)
        self._bracket_list[index][1] = score
        
    # Update Bracket to hold the winner of a match    
    def update_winner(self, player, round):
        if round >= self.max_round() or round < 0: return None # invalid round

        new_index = self.player_index_by_round(player, round+1)
        self._bracket_list[new_index] = [player, 0]

    # Return bracketlist state as string
    def to_string(self):
        return str(self._bracket_list)
        

#-----------------------------------------------------------------------

def main():
    players = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7']
    bracket = Bracket(players)

    print("Num players: %d" % (bracket.num_players()))
    print('')
    print("Players: ", end='')
    print(bracket.players())
    print('')
    print("To string: " + bracket.to_string())
    print('')
    print("First index of round 0: " + str(bracket.first_index_of_round(0)))
    print("First index of round 1: " + str(bracket.first_index_of_round(1)))
    print("First index of round 2: " + str(bracket.first_index_of_round(2)))
    print("First index of round 3: " + str(bracket.first_index_of_round(3)))
    print("First index of round 4: " + str(bracket.first_index_of_round(4)))
    print("First index of round 5: " + str(bracket.first_index_of_round(5)))
    print('')
    print("P3 index of round 0: " + str(bracket.player_index_by_round("P3", 0)))
    print("P3 index of round 1: " + str(bracket.player_index_by_round("P3", 1)))
    print("P3 index of round 2: " + str(bracket.player_index_by_round("P3", 2)))
    print("P3 index of round 3: " + str(bracket.player_index_by_round("P3", 3)))
    print("P3 index of round 4: " + str(bracket.player_index_by_round("P3", 4)))
    print("P3 index of round 5: " + str(bracket.player_index_by_round("P3", 5)))
    print('')
    bracket.update_score("P3", 0, 75)
    bracket.update_winner("P3", 0)
    print("To string: " + bracket.to_string())
    print('')
    return

#-----------------------------------------------------------------------
if __name__ == '__main__':
    main()