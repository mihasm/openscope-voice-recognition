"""Main application, which uses an Tx button to record the user's voice,
and generate the appropriate commands as per OpenScope specification.

Attributes:
    a (TYPE): Description
    AIRLINES (TYPE): Description
    COMMANDS (TYPE): Description
    i (int): Description
    NUMS (TYPE): Description
    PHON (TYPE): Description

Deleted Attributes:
    expected_words_callsign (TYPE): Description
"""
import keyboard  # using module keyboard
from difflib import get_close_matches
import pyperclip
from listen_method import AudioRecognizer
import json
import speech_recognition as sr
import re
from loaders import load_airlines, load_phonetics, load_numbers
from difflib import SequenceMatcher
from word2number import w2n

AIRLINES = load_airlines()
PHON = load_phonetics()
NUMS = load_numbers()

def parse_phonetics(text):
    """Summary
    
    Args:
        text (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    for k in PHON.keys():
        if k in text:
            text = text.replace(k,PHON[k])
    return text

def parse_airlines(text):
    """Summary
    
    Args:
        text (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    for k in AIRLINES.keys():
        if k in text:
            text = text.replace(k,AIRLINES[k])
    return text

def parse_numbers(text):
    """Summary
    
    Args:
        text (TYPE): Description
    
    Returns:
        TYPE: Description
    """
    for k in NUMS.keys():
        if k in text:
            text = text.replace(k,NUMS[k])
    return text


COMMANDS = [
    [r"turn left heading (\d\d\d)", r"t l \1"],
    [r"turn right heading (\d\d\d)", r"t r \1"],
    [r"turn left (\d\d) degrees", r"t l \1"],
    [r"turn right (\d\d) degrees", r"t r \1"],
    [r"fly heading (\d\d\d)", r"fh \1"],
    ["fly present heading", "fph"],
    ["cleared as filed", "caf"],
    [r"climb to flight level (\d\d\d?)", r"c \1"],
    [r"descend to flight level (\d\d\d?)", r"d \1"],
    ["report speed", "si"],
    ["report heading", "sh"],
    ["report altitude", "sa"],
    [r"squawk (\d\d\d\d)", r"sq \1"],
    ["climb via sid", "cvs"],
    ["cleared for takeoff", "cro"],
    [r"taxi to runway (\d\d(L|R|C)?)", r"taxi \1"],
    [r"expect runway (\d\d(L|R|C)?)", r"e \1"],
    [r"descend via star", r"dvs"],
    [r"clear for ILS approach runway (\d\d(L|R|C)?)", r"i \1"],
]

def prepare_commands_list():
    i = 0
    for k, c in COMMANDS:
        command = ""
        for w in k.split(" "):
            w = w.strip()
            if not w == "":
                if w.isalpha():
                    command += " " + w
                    command = command.strip()

        COMMANDS[i].append(command)
        i += 1
prepare_commands_list()

def similar(a, b):
    """Returns the similarity ratio between strings a and b.
    
    Args:
        a (str): String a
        b (str): String b
    
    Returns:
        float: Similarity
    """
    return SequenceMatcher(None, a, b).ratio()


def split_recognized_text_into_callsign_command(recognized_text):
    """Receives the raw recognized text from voice recognition,
    and splits the text into two parts. The first part is the
    callsign portion of the message, the second part is the
    instruction portion of the message.
    
    Args:
        recognized_text (str): Raw text from voice recognition.
    
    Returns:
        tuple: (command portion, callsign portion, most similar command from COMMANDS)
    """
    # Get list of lists where first element is similarity score
    # and second element is index of command.
    lst_compare = []
    for i in range(len(COMMANDS)):
        p = COMMANDS[i][2]
        ratio = similar(p, recognized_text)
        lst_compare.append([ratio, i])

    # Sort the list to get the most similar command.
    lst_compare = sorted(lst_compare, key=lambda x: x[0])
    lst_compare.reverse()
    most_sim_command = COMMANDS[lst_compare[0][1]]
    print("Most similar command:", most_sim_command)

    # Detect start of command.
    # First, split the sentence into all possible starts,
    # then compare the similarity between the remaining sentence,
    # and the most similar command from above.
    lst_compare = []
    string_words = recognized_text.split(" ")
    for i in range(len(string_words)):
        cut = " ".join(string_words[i:])
        # TOCHECK: most_sim_command[3] it probably only the string part?
        similarity = similar(most_sim_command[2], cut)
        lst_compare.append([similarity, i])
    lst_compare = sorted(lst_compare, key=lambda x: x[0])
    lst_compare.reverse()

    # Gets probably command part and callsign part of the speech recognized text

    command_part = " ".join(string_words[lst_compare[0][1]:])
    callsign_part = " ".join(string_words[:lst_compare[0][1]])

    return command_part.lower(),callsign_part.lower(),most_sim_command

def parse_command_portion(command_part,most_sim_command):
    """Parses the command portion of the raw recognition text.
    
    Args:
        command_part (str): Command portion of the raw recognition text.
        most_sim_command (tuple): Most similar command from COMMANDS
    
    Returns:
        str: Command as per OpenScope specification
    """
    command_part = command_part.lower()
    command_part = parse_numbers(command_part)
    command_part = parse_phonetics(command_part)
    command_part = command_part.replace("heading to","heading 2")
    command_part = re.sub(r"(\d+)\s+(?=\d)",r"\1",command_part)

    # parse left,right,center
    command_part = re.sub(r"(\d+) right",r"\1R",command_part)
    command_part = re.sub(r"(\d+) left",r"\1L",command_part)
    command_part = re.sub(r"(\d+) center",r"\1C",command_part)
    command_part = re.sub(r"(\d+) centre",r"\1C",command_part)

    # Get numbers from command and callsign in order
    numbers_command = re.findall(r"\d+[RLC]?", command_part)

    # Insert number into actual command
    insert_spots = re.findall(r"\\\d+[RLC]?", most_sim_command[1])
    out_command = most_sim_command[1]
    i = 0
    for insert_spot in insert_spots:
        if len(numbers_command) >= i+1:
            out_command = out_command.replace(insert_spot, numbers_command[i])
        else:
            out_command = out_command.replace(insert_spot, "")
        i += 1
    
    return out_command


def parse_callsign_portion(callsign_part):
    """Parses the callsign portion of the raw recognition text.
    
    Args:
        callsign_part (str): Callsign portion of the raw recognition text.
    
    Returns:
        str: Callsign, shortened to ICAO standard
    """
    callsign_part = callsign_part.lower()
    callsign_part = re.sub(r'[^a-zA-Z0-9 ]', '', callsign_part)
    callsign_part = parse_numbers(callsign_part)
    callsign_part = callsign_part.replace(" to "," 2 ")
    callsign_part = parse_airlines(callsign_part)
    callsign_part = parse_phonetics(callsign_part)

    m = re.match(r"([a-z]+ ?)+",callsign_part)
    if m:
        # first match will probably be an airline
        text_to_replace = m.group(0)
        lst_compare = []
        string_words = list(AIRLINES.keys())
        for i in range(len(string_words)):
            similarity = similar(string_words[i],text_to_replace)
            lst_compare.append([similarity, string_words[i]])
        lst_compare = sorted(lst_compare, key=lambda x: x[0])
        lst_compare.reverse()
        probably_airline = lst_compare[0][1]
        print("Probable airline:",probably_airline)
        callsign_part = callsign_part.replace(text_to_replace,AIRLINES[probably_airline])
    callsign_part = callsign_part.replace("heavy","") # remove heavy as it is not important
    callsign_part = re.sub(r"([a-z]+ ?)+","",callsign_part) # replace all other lowercase string occurences

    callsign_part = callsign_part.replace(" ","")
    print("Generated callsign:",callsign_part)
    return callsign_part


def parse_voice(recognized_text):
    """Receives the recognized text from voice recognition,
    and calls all other functions needed for parsing it,
    finally returning the complete command,
    prepared for issuing into OpenScope.
    
    Args:
        recognized_text (str): Raw voice recognized command
    
    Returns:
        str: Formatted OpenScope command
    """

    # Parse common number errors

    command_part,callsign_part,most_sim_command = split_recognized_text_into_callsign_command(recognized_text)

    print("Command part:", command_part)
    print("Callsign part:", callsign_part)

    out_callsign = parse_callsign_portion(callsign_part)
    out_command = parse_command_portion(command_part,most_sim_command)
    
    out = out_callsign+" "+out_command
    print("Output:", out)
    print("==================")
    return out


def on_recognition_success(text, paste_from_clipboard=True):
    """Helper function that is used by the AudioRecognizer class
    to call the voice parsing function when the audio stops recording,
    and the voice recognition engine does its job.
    
    Args:
        text (str): Text from voice recognition
        paste_from_clipboard (bool, optional): Enables/Disables game integration
    """
    command = parse_voice(text)
    if paste_from_clipboard:
        pyperclip.copy(command)
        keyboard.press_and_release('ctrl+a')
        keyboard.press_and_release('delete')
        keyboard.press_and_release('ctrl+v')
        keyboard.press_and_release('enter')


a = AudioRecognizer(on_recognition_success)
a.start()

#s = "delta 225 to clear for the aisle S roach runway 25"
#com = parse_voice(s)
# print(com)
