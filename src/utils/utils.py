#! usr/bin/env python

#-----------------------------------------------------------------------
# utils.py
# Authors: BracketMaker Team
#-----------------------------------------------------------------------

def closest_power_of_two(num):
    power_of_two = 1
    while power_of_two < num:
        power_of_two *= 2
    return power_of_two

#-----------------------------------------------------------------------