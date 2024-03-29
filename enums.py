from enum import Enum

class characterClass(Enum):
    SHADOW_WARLOCK = 1
    FIRE_WARLOCK = 2
    SHADOW_PRIEST = 3
    UNKNOWN = 4

class composition(Enum):
    W1_0SP = 1
    W2_0SP = 2
    W3_0SP = 3
    W4_0SP = 4
    W5_0SP = 5
    W1_1SP = 6
    W2_1SP = 7
    W3_1SP = 8
    W4_1SP = 9
    W5_1SP = 10
    UNKNOWN = 11
    W1_2SP = 12
    W2_2SP = 13
    W3_2SP = 14
    W4_2SP = 15
    W5_2SP = 16
    W1_3SP = 17
    W2_3SP = 18
    W3_3SP = 19
    W4_3SP = 20
    W5_3SP = 21

def compToNum(comp):
    if comp == str(composition.W1_0SP):
        return 1
    if comp == str(composition.W2_0SP):
        return 2
    if comp == str(composition.W3_0SP):
        return 3
    if comp == str(composition.W4_0SP):
        return 4
    if comp == str(composition.W5_0SP):
        return 5
    if comp == str(composition.W1_1SP):
        return 2
    if comp == str(composition.W2_1SP):
        return 3
    if comp == str(composition.W3_1SP):
        return 4
    if comp == str(composition.W4_1SP):
        return 5
    if comp == str(composition.W5_1SP):
        return 6
    if comp == str(composition.W1_2SP):
        return 3
    if comp == str(composition.W2_2SP):
        return 4
    if comp == str(composition.W3_2SP):
        return 5
    if comp == str(composition.W4_2SP):
        return 6
    if comp == str(composition.W5_2SP):
        return 7
    if comp == str(composition.W1_3SP):
        return 4
    if comp == str(composition.W2_3SP):
        return 5
    if comp == str(composition.W3_3SP):
        return 6
    if comp == str(composition.W4_3SP):
        return 7
    if comp == str(composition.W5_3SP):
        return 8






