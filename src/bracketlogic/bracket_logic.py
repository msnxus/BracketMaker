#! usr/bin/env python

#-----------------------------------------------------------------------
# bracket_logic.py
# Authors: BracketMaker Team
#-----------------------------------------------------------------------

# ASK SAM
import sys
import os

# Add the parent directory to the Python path
utilsdir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../utils'))
sys.path.append(utilsdir)

from utils import utilss

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
            self._bracket_list.append((player, 0))
        # Append None for the winners of all games
        for i in range(bracket_size-1):
            self._bracket_list.append(None)

    # Helper function
    def locate_position_in_list(self, player, round):
        initial_index = self._bracket_list
        return

    # Getter functions
    def num_players(self):
        return self._bracket_list[0]
    
    def players(self):
        bracket_size = closest_power_of_two(self.num_players())
        players = []
        for i in range(bracket_size):
            players.append(self._bracket_list[i+1])

    # Update functions
    def update_score(player, round, score):
        list_position = locate_position_in_list(self, player, round)
        self._bracketList[list_position] = score
        
    # Update Bracket to hold the winner of a match    
    def update_winner(player, round):
        

#-----------------------------------------------------------------------

def main():
    # unit testing
    return

#-----------------------------------------------------------------------
if __name__ == '__main__':
    main()