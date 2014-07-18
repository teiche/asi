# Astronomy related helper functions

import logging
import math

logger = logging.getLogger(__name__)

SPECTRAL_LETTER_MAP = {
    'O' : 00,
    'B' : 10,
    'A' : 20,
    'F' : 30,
    'G' : 40,
    'K' : 50,
    'M' : 60,
    'L' : 70,
    'T' : 80,
    'Y' : 90,
}

def stype_to_number(stype):
    """
    Given a python string of length 2 representing a Stellar Spectral Type,
    convert it to a numerical representation that can be sorted

    The detailed of the numerical representation are unimportant, but are:

    The letter becomes the tens digit of a number between 0 and 99, and the number
    becomes the ones digit directly

    The letters are mapped O -> 0, B -> 1 ... Y -> 9

    Lower numbers are hotter

    If stype is not a valid spectral type, a high number is returned and a warning issued
    This prevents the star from being selected for anything unless it's the only option
    while allowing the system to continue operating
    """
    try:
        return SPECTRAL_LETTER_MAP[stype[0]] + int(stype[1])

    except:
        logger.warning("Invalid spectral type {stype}.".format(stype=stype))
        return 999

    
def dist(s1, s2):
    """
    Given two objects s1 and s2(these can be either SingleStar or DoubleStar instances), 
    return the angular Euclidean distance between them
    """
    return math.sqrt((s1.ra_deg - s2.ra_deg)**2 + (s1.dec_deg - s2.dec_deg)**2)
