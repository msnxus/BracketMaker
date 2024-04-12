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
# import src.database
# -------------- UNCOMMENT THIS TO RUN LOCALLY --------------
import database

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
        print('bracketsize', bracketsize)

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
            if binary_string is '':
                binary_string = '0'
            decimal_value = int(binary_string, 2) + 1
            result.append(decimal_value)
        return result

    
    def __create_matchups__(temp_teams, bracket_size):
        ordering = Bracket.__seed__(bracket_size)
        print('ordering:', ordering)
        final = []
        for i in range(bracket_size):
            final.append([temp_teams[ordering[i]-1], 0])
        print("---------------",final)


        # print(Bracket.__seed__(temp_teams))
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
        # print(temp_teams)
        # Enter players into real bracket based on matchup (1-16, 2-15, ...)
        # NEXT STEP: Want it to be (1-16, 8-9 ... 7-10, 2-15)
        

        output = Bracket.__create_matchups__(temp_teams, bracket_size)
        print(output)
        
        print(self._bracket_list)
        print("TEST!!!!")
        self._bracket_list += output
        print(self._bracket_list)
        for i in range(bracket_size-1):
            self._bracket_list.append(None)
        print(self._bracket_list)
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
        print(self._bracket_list)
        return self._bracket_list
    
    # Return a list specifying the beggining and ending indicies of a round
    # as [round][lower index, higher index]
    def round_indicies(self):
        round_indicies = []
        for round in range(self.max_round() - 1):
            round_indicies.append([self.first_index_of_round(round), self.first_index_of_round(round + 1) -1])

        round_indicies.append([self.first_index_of_round(self.max_round() - 1), self.first_index_of_round(self.max_round() - 1) + 1])
        print(round_indicies)
        return round_indicies
    # Return max round
    def max_round(self):
        return int(math.log(closest_power_of_two(self.num_players()), 2))


    # Update functions
    def update_score(self, player, round, score):
        if round >= self.max_round() or round < 0: return None # invalid round

        index = self.player_index_by_round(player, round)
        print("player and round:", player, round)
        print("player index:", index)
        self._bracket_list[index][1] = score
        
        
    # Update Bracket to hold the winner of a match   
    def update_winner(self, player, round):
        if round >= self.max_round() or round < 0: return None # invalid round

        new_index = self.player_index_by_round(player, round+1)
        if self._bracket_list[new_index] == None:
            self._bracket_list[new_index] = [player, 0]
        elif self._bracket_list[new_index][0] != player:
            self._bracket_list[new_index] = [player, 0]
            

    #Format the names of the bracket in a friendly way to be displayed in
    # a grid.  The players will be ordered by 
    # (player 1, round 1) (player 1, round 2) ... (player 2, round 1) (player 2 round 2) ....
    def grid_friendly_players(self):
        grid_friendly_players = []

        print("Players: ", self.num_players())
        print("Rounds: ", self.max_round())

        ignored_rounds = -1
        for player_index in range(self.num_players()):
            if player_index == 1:
                ignored_rounds += 1
            if (player_index) % 2 == 0:
                ignored_rounds += 1

            for round in range(self.max_round() + 1):
                if (round < (self.max_round() +1) - ignored_rounds):
                    index = self.first_index_of_round(round) + player_index
                    grid_friendly_players.append(self._bracket_list[index])
                    print("normal", index)

                else:
                    grid_friendly_players.append(["blank", 0])
                    print("blank")

        print (grid_friendly_players)
        return grid_friendly_players



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

    #Stores this bracket in the database
    def store(self, code):
        ser = self.serialize()
        database.create_bracket(code, ser)

    #Retrieves bracket with said code from database
    def load(self, code):
        data = database.get_bracket_from_code(code)
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
                else: print("TIE!")
            print('')
        print("set winners",self.to_string())
        # print("hopefully dif", ret_bracket.to_string())
        return

        

    # Determine winner of a match
    def determine_winner(self, player1, player2, round):
        # checks if valid players are entered - this is tough because
        # we need to ensure they are both in the same round and adjacent
        # meaning they play against each other

        # checks if valid players are entered
        if round >= self.max_round() or round < 0: return None # invalid round
        if player1 != self._bracket_list[self.player_index_by_round(player1, round)][0]:
            print("AHHHHHH1")
            return None
        if player2 != self._bracket_list[self.player_index_by_round(player2, round)][0]:
            print("AHHHHHH2")
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
        

#-----------------------------------------------------------------------

def main():
    players = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7']
    bracket = Bracket("hi", players)

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
    print('Testing Bracket Flow')
    bracket.update_score("P3", 0, 75)
    bracket.update_score("P4", 0, 50)
    print("P3 score in round 0:", bracket.get_score("P3", 0))
    print("P4 score in round 0:", bracket.get_score("P4", 0))
    print("The winner of this matchup is:", bracket.determine_winner("P3","P4", 0))
    bracket.update_winner(bracket.determine_winner("P3","P4", 0), 0)

    print("Updated Bracket:")
    print("To string: " + bracket.to_string())

    bracket.update_score("P1", 0, 15)
    bracket.update_score("P2", 0, 100)
    print("P1 score in round 0:", bracket.get_score("P1", 0))
    print("P2 score in round 0:", bracket.get_score("P2", 0))
    print("The winner of this matchup is:", bracket.determine_winner("P1","P2", 0))
    bracket.update_winner(bracket.determine_winner("P1","P2", 0), 0)
    
    print("Updated Bracket:")
    print("To string: " + bracket.to_string())

    bracket.update_score("P2", 1, 275)
    bracket.update_score("P3", 1, 305)
    print("P2 score in round 0:", bracket.get_score("P2", 1))
    print("P3 score in round 0:", bracket.get_score("P3", 1))
    print("The winner of this matchup is:", bracket.determine_winner("P2","P3", 1))
    bracket.update_winner(bracket.determine_winner("P2","P3", 1), 1)


    print("Updated Bracket:")
    print("To string: " + bracket.to_string())
    print('')



    # TEST FOR BYE - should automatically put P7 into next round because
    # P7 has no 0 round opponent
    # bracket.update_score("P7", 0, 100)
    # print("P7 score in round 0:", bracket.get_score("P7", 0))
    # print("The winner of this matchup is:", bracket.determine_winner("P7","P4", 0))
    # bracket.update_winner(bracket.determine_winner("P3","P4", 0), 0)

    print("Bracket complete?", bracket.is_complete())
    return

#-----------------------------------------------------------------------
if __name__ == '__main__':
    main()