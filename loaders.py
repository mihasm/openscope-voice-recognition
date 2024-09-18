"""Summary
"""
import json


def load_airlines():
    """Summary
    
    Returns:
        TYPE: Description
    """
    f = open("airlines.json","rb")
    txt = f.read().decode()
    d = json.loads(txt)
    out = {}
    for a_d in d:
        out[a_d["callsign"].lower()]=a_d["icao"]
    return out


def load_phonetics():
    """Summary
    
    Returns:
        TYPE: Description
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
    """Summary
    
    Returns:
        TYPE: Description
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
