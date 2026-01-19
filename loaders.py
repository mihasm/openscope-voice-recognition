"""Data loading utilities for OpenScope Voice Recognition.

This module provides functions to load airline, phonetic, and number mapping data
from external files into dictionaries for use by the voice recognition system.
"""
import json


def load_airlines():
    """Load airline callsign to ICAO code mappings from airlines.json.

    Returns:
        dict: Dictionary mapping airline callsigns to ICAO codes
    """
    f = open("airlines.json","rb")
    txt = f.read().decode()
    d = json.loads(txt)
    out = {}
    for a_d in d:
        out[a_d["callsign"].lower()]=a_d["icao"]
    return out


def load_phonetics():
    """Load NATO phonetic alphabet mappings from phonetic_icao.txt.

    Returns:
        dict: Dictionary mapping phonetic words to letters
    """
    out = {}
    f = open("phonetic_icao.txt","r")
    lines = f.readlines()
    for l in lines:
        l = l.strip()
        words = l.split(",")
        letter = words[0]
        for w in words[1:]:
            if w != "":
                w = w.lower()
                out[w] = letter
    return out

def load_numbers():
    """Load number pronunciation mappings from phonetic_numbers.txt.

    Returns:
        dict: Dictionary mapping number words to digits
    """
    out = {}
    f = open("phonetic_numbers.txt","r")
    lines = f.readlines()
    for l in lines:
        l = l.strip()
        words = l.split(",")
        letter = words[0]
        for w in words[1:]:
            if w != "":
                w = w.lower()
                out[w] = letter
    return out
