#! usr/bin/env python

#-----------------------------------------------------------------------
# bracket_logic.py
# Authors: BracketMaker Team
#-----------------------------------------------------------------------

import math

# ASK SAM
import sys
import os
import json
# -------------- COMMENT THIS OUT TO RUN LOCALLY --------------
import src.database
# -------------- UNCOMMENT THIS TO RUN LOCALLY --------------
# import database

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
    def __init__(self, name, players):
        self._bracket_list = []
        self.name = name
        self.init_bracket(players)
        return
    
    # Get ordering of indices
    def __seed__(bracketsize):
        nbr_bits_required = len(bin(bracketsize)) - 3
        binary_seeds = [[0] * nbr_bits_required for _ in range(bracketsize)]

        for i in range(nbr_bits_required):
            binary_seeds[0][i] = 0

        for col in range(nbr_bits_required):
            for row in range(1, bracketsize):
                if row % (2 ** (col + 1)) == 0:
                    binary_seeds[row][col] = binary_seeds[row - 1][col]
                else:
                    binary_seeds[row][col] = 1 if binary_seeds[row - 1][col] == 0 else 0

        result = []
        for i in range(bracketsize):
            binary_string = ''.join(map(str, binary_seeds[i]))
            if binary_string == '':
                binary_string = '0'
            decimal_value = int(binary_string, 2) + 1
            result.append(decimal_value)
        return result

    
    def __create_matchups__(temp_teams, bracket_size):
        ordering = Bracket.__seed__(bracket_size)
        final = []
        for i in range(bracket_size):
            final.append([temp_teams[ordering[i]-1], 0])
        return final

  
    def init_bracket(self, players):
        teams = len(players)
        bracket_size = closest_power_of_two(teams)
        self._bracket_list.append(teams)
        i = 0

        # Add the plaers and byes in order. Should be power of two's
        temp_teams = []
        for player in players:
            temp_teams.append(player)
            i += 1
        # Append None for missing teams of all games
        for j in range(bracket_size-i):
            temp_teams.append("Bye")
        # Enter players into real bracket based on matchup (1-16, 2-15, ...)
        # NEXT STEP: Want it to be (1-16, 8-9 ... 7-10, 2-15)
        

        output = Bracket.__create_matchups__(temp_teams, bracket_size)
        self._bracket_list += output
        for i in range(bracket_size-1):
            self._bracket_list.append(None)
        # return self._bracket_list NO NEED TO RETURN 

    # Given player and round return index in underlying bracketlist
    # If nonreal round or nonexistent player return None
    def player_index_by_round(self, player, round):
        if round > self.max_round() or round < 0: return None # nonreal round

        initial_index = 0
        for i in range(closest_power_of_two(self.num_players())):
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

    # Return the name of this bracket
    def name(self):
        return self.name
    
    # Return list of all player names
    def players(self):
        players = []
        for i in range(self.num_players()):
            players.append(self._bracket_list[i+1][0]) # tuple, only return name
        return players
    
    # Return bracket list
    def bracket_list(self):
        return self._bracket_list
    
    # Return a list specifying the beggining and ending indicies of a round
    # as [round][lower index, higher index]
    def round_indicies(self):
        round_indicies = []
        for round in range(self.max_round() - 1):
            round_indicies.append([self.first_index_of_round(round), self.first_index_of_round(round + 1) -1])

        round_indicies.append([self.first_index_of_round(self.max_round() - 1), self.first_index_of_round(self.max_round() - 1) + 1])
        return round_indicies
    # Return max round
    def max_round(self):
        return int(math.log(closest_power_of_two(self.num_players()), 2))


    # Update functions
    def update_score(self, player, round, score):
        if round >= self.max_round() or round < 0: return None # invalid round

        index = self.player_index_by_round(player, round)
        self._bracket_list[index][1] = score
        
        
    # Update Bracket to hold the winner of a match   
    def update_winner(self, player, round):
        if round >= self.max_round() or round < 0: return None # invalid round

        new_index = self.player_index_by_round(player, round+1)
        if self._bracket_list[new_index] == None:
            self._bracket_list[new_index] = [player, 0]
        elif self._bracket_list[new_index][0] != player:
            old_player = self._bracket_list[new_index][0]
            self._bracket_list[new_index] = [player, 0]
            # set the opposing players score to 0
            if new_index % 2 == 1:
                if(new_index + 1 < len(self._bracket_list)):
                    self._bracket_list[new_index + 1][1] = 0
            else:
                self._bracket_list[new_index - 1][1] = 0
            opps = self.get_all_opposing_players(old_player, round+1)
            for opp in opps:
                self._bracket_list[opp[1]] = None

    def get_all_opposing_players(self, start_player, start_round):
        all_players = [[start_player, start_round]]
        start_round += 1
        for player in all_players:
            new_index = self.player_index_by_round(player[0], start_round)
            if new_index != None:
                if self._bracket_list[new_index] != None:
                    if start_round == self.max_round():
                        all_players.append([self._bracket_list[new_index][0], new_index])
                        break
                    print([self._bracket_list[new_index][0], new_index])
                    all_players.append([self._bracket_list[new_index][0], new_index])
                    if new_index % 2 == 1:
                        if self._bracket_list[new_index + 1] != None:
                            all_players.append([self._bracket_list[new_index + 1][0], new_index + 1])
                    else:
                        if self._bracket_list[new_index - 1] != None:
                            all_players.append([self._bracket_list[new_index - 1][0], new_index - 1])
            start_round += 1
            # if start_round == self.max_round():
            #     break
         
        return all_players[1:]

    #Formatting and storage functions
    # Return bracketlist state as string
    def to_string(self):
        return str(self._bracket_list)
    
    # serialize the bracket into a string
    def serialize(self):
        ser = []
        ser.append(self.name)
        ser.append(self._bracket_list)
        return json.dumps(ser)

    # return a bracket object represented by the string
    def deserialize(self, string):

        deser = json.loads(string)
        self.name = deser[0]
        self._bracket_list = deser[1]

    #Stores this bracket in the data base
    def store(self, code, name, teams, netid, player_updates):
        ser = self.serialize()
        return src.database.create_bracket(code, name, teams, ser, netid, player_updates)

    #Retrieves bracket with said code from database

    def update(self, code):
        ser = self.serialize()
        # src.database.update_bracket(code, ser)
        src.database.update_bracket(code, ser)

    
    def load(self, code):
        data = src.database.get_bracket_from_code(code)
        if data != False:
            data = data[0]
            self.name = data[0]
            self._bracket_list = data[1]

        
    def get_round(self, index):
        num_teams = self._bracket_list[0]
        bracket_size = closest_power_of_two(num_teams)
        max_index_for_round = 0
        round = 0
        while bracket_size != 1:
            max_index_for_round += bracket_size
            if index < max_index_for_round:
                return round 
            bracket_size = int(bracket_size/ 2)
            round += 1

    # Loop through the entire bracket and determine the winners of
    # each round
    def set_winners(self):
        for i in range(1, len(self._bracket_list)-1, 2):
            if self._bracket_list[i] is not None and self._bracket_list[i+1] is not None:
                round = self.get_round(i)
                player1 = self._bracket_list[i][0]
                player2 = self._bracket_list[i+1][0]
                bye = self.has_bye(player1, round)
                if bye == 1:
                    winner = player1
                elif bye == 0:
                    winner = player2
                else:
                    winner = self.determine_winner(player1, player2, round)
                if winner != "tie":
                    self.update_winner(winner, round)
        return

        

    # Determine winner of a match
    def determine_winner(self, player1, player2, round):
        # checks if valid players are entered - this is tough because
        # we need to ensure they are both in the same round and adjacent
        # meaning they play against each other

        # checks if valid players are entered
        if round >= self.max_round() or round < 0: return None # invalid round
        if player1 != self._bracket_list[self.player_index_by_round(player1, round)][0]:
            return None
        if player2 != self._bracket_list[self.player_index_by_round(player2, round)][0]:
            return None

        # need to check if the players actually play against one another
        score1 = self.get_score(player1, round)
        score2 = self.get_score(player2, round)

        if score1 > score2: return player1
        elif score2 > score1: return player2
        else: return "tie"

    # Get score of a player after a round 
    def get_score(self, player, round):
        if round >= self.max_round() or round < 0: return None # invalid round

        index = self.player_index_by_round(player, round)
        return int(self._bracket_list[index][1])

    # Determines if bracket is complete based on if there is a champion
    def is_complete(self):
        if self._bracket_list[len(self._bracket_list) - 1] is None:
            return False
        return True
    
    # Checks if a player has a BYE
    # Invariant - player will always be listed before the empty bye slot
    def has_bye(self, player, round):
        if round >= self.max_round() or round < 0: return None # invalid round

        index = self.player_index_by_round(player, round)

        # Checks is player is last in the round

        #checks if subsequent index is None to see if the player has a bye
        if self._bracket_list[index+1][0] == "Bye":
            return 1 # Player against is BYE
        elif player == "Bye":
            return 0 # Player is BYE
        return 2 # No BYEs