import keyboard  # using module keyboard
from difflib import get_close_matches
import pyperclip
from listen_method import listen2
import json
import speech_recognition as sr
import re
from loaders import load_airlines, load_phonetics, load_numbers
import jellyfish
from difflib import SequenceMatcher


BUTTON = "shift"

airlines = load_airlines()
phon = load_phonetics()
nums = load_numbers()

expected_words_callsign = []
for a in airlines.keys():
    expected_words_callsign.append(a.lower())
for p in phon.keys():
    expected_words_callsign.append(p.lower())

def parse_phonetics(text):
    text = text.lower()
    for k in phon.keys():
        if k in text:
            text = text.replace(k,phon[k])
    return text

def parse_airlines(text):
    text = text.lower()
    for k in airlines.keys():
        if k in text:
            text = text.replace(k,airlines[k])
    return text

def parse_numbers(text):
    text = text.lower()
    for k in nums.keys():
        if k in text:
            text = text.replace(k,nums[k])
    return text

def parse_number_errors(text):
    text = re.sub(r"to (\d)",r"2\1",text)
    text = re.sub(r"9er",r"9",text)
    text = re.sub(r"9 re",r"9",text)
    text = re.sub(r"9 or",r"9",text)
    text = re.sub(r"niners",r"9",text)
    text = re.sub(r"9 north",r"9",text)
    text = re.sub(r"(\d) to",r"\1|2",text)
    text = re.sub(r"(\d)th",r"\1",text)
    return text


def parse_airline(text):
    print("Parsing airline:",text)

    airline_text = text

    # remove phonetics
    for w in phon.keys():
        if w.lower() in airline_text.lower():
            airline_text = airline_text.replace(w.lower(),"")

    # remove numbers
    airline_text = re.sub(r'[0-9]+', '', airline_text)

    airline_text = airline_text.strip()
    
    if not airline_text.isnumeric() and not airline_text == "":
        similar = get_close_matches(airline_text,expected_words_callsign)
        if len(similar) > 0:
            match = similar[0]
            text = text.replace(airline_text, airlines[match])
        else:
            return None

    

    text = parse_phonetics(text)

    text = "".join(text.split(" ")).upper()

    return text

def parse_commands(text):
    text = text.lower()
    text = parse_numbers(text)
    text = re.sub(r'\W+', ' ', text)
    text = parse_number_errors(text)
    text = re.sub(r"(\d) (\d)",r"\1\2",text)
    text = re.sub(r"(\d) (\d)",r"\1\2",text)
    text = re.sub(r"(\d) (\d)",r"\1\2",text)
    text = re.sub(r"(\d) (\d)",r"\1\2",text)
    print("Replaced:",text)

    command_detected = False


    for c in commands.keys():
        res = re.search(c,text.lower())
        if res:
            if command_detected == False:
                command_detected = True
                span = res.span()
                callsign = text[:span[0]]
                command = text[span[0]:]
                issued_command = re.sub(c,commands[c],command)
                break

    if command_detected:

        res = parse_airline(callsign)
        
        if res == None:
            callsign = parse_airlines(callsign)
            callsign = parse_phonetics(callsign)
            callsign = "".join(callsign.split(" ")).upper()
        else:
            callsign = res

        if callsign[0] == "D":
            callsign = "DAL"+callsign[1:]
        
        print("Callsign:",callsign)
        print("Command:", command)

        combined_command = callsign +" "+ issued_command
        
        print("Issued command:",combined_command)
        return combined_command


    else:
        print("Command not detected...")

class AudioRecognizer:

    def start(self):
        r = sr.Recognizer()
        r.listen = listen2

        def set_pressed():
            print("Recording started...")
            audio = r.listen(r,source)
            print("Recording finished...")
            # recognize speech using Google Speech Recognition
            try:
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`
                text = r.recognize_google(audio)
                print(">>" + text)
                #command = parse_commands(text)
                #pyperclip.copy(command)
                #keyboard.press_and_release('ctrl+v')
                #keyboard.press_and_release('enter')
                parse_command_with_string_comparison(text)

            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

        with sr.Microphone() as source:
            print("Adjusting for ambient noise, be quiet!")
            r.adjust_for_ambient_noise(source)  # listen for 1 second to calibrate the energy threshold for ambient noise levels

            print("Waiting for key press...")
            keyboard.add_hotkey(BUTTON,lambda: set_pressed())
            keyboard.wait()

commands = [
    [r"turn left heading (\d\d\d)",r"t l \1"],
    [r"turn right heading (\d\d\d)",r"t r \1"],
    [r"turn left (\d\d) degrees",r"t l \1"],
    [r"turn right (\d\d) degrees",r"t l \1"],
    [r"fly heading (\d\d\d)",r"fh \1"],
    ["fly present heading","fph"],
    ["cleared as filed","caf"],
    [r"climb to flight level (\d\d\d?)",r"c \1"],
    [r"descend to flight level (\d\d\d?)",r"d \1"],
    ["report speed","si"],
    ["report heading","sh"],
    ["report altitude","sa"],
    [r"squawk (\d\d\d\d)",r"sq \1"],
    ["climb via sid","cvs"],
    ["cleared for takeoff","cro"],
    [r"taxi to runway (\d\d(L|R|C)?)",r"taxi \1"],
    [r"expect runway (\d\d(L|R|C)?)",r"e \1"],
    [r"descend via star",r"dvs"],
    [r"clear for ILS approach runway (\d\d(L|R|C)?)",r"dvs"],
]

words = set()

i = 0
for k,c in commands:
    command = ""
    for w in k.split(" "):
        w = w.strip()
        if not w == "":
            if w.isalpha():
                command += " " + w
                command = command.strip()

    commands[i].append(jellyfish.metaphone(command))
    commands[i].append(command)
    i+=1

for k,c,p,_ in commands:
    for w in k.split(" "):
        w = w.strip()
        if not w == "":
            if w.isalpha():
                words.add(w)

for k in airlines.keys():
    k = k.strip()
    if not k == "":
        words.add(k)

for k in phon.keys():
    k = k.strip()
    if not k == "":
        words.add(k)

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def parse_command_phonetically(s):
    m = jellyfish.metaphone(s)
    print("Command phonetic:",m)

    lst_compare = []

    for i in range(len(commands)):
        p = commands[i][2]
        jaro_comp = similar(p,m)
        lst_compare.append([jaro_comp,i])

    lst_compare = sorted(lst_compare, key=lambda x: x[0])
    lst_compare.reverse()

    print("Most similar command:",commands[lst_compare[0][1]])
    print("Most similar command phonetic:",commands[lst_compare[0][1]][2])
    print("Score:",lst_compare[0][0])

    # detect start of command
    most_sim_com_phonetic = commands[lst_compare[0][1]][2]

    lst_compare = []

    string_words = s.split(" ")
    for i in range(len(string_words)):
        cut = " ".join(string_words[i:])
        cut_phon = jellyfish.metaphone(cut)
        similarity = similar(most_sim_com_phonetic,cut_phon)
        lst_compare.append([similarity,i])

    lst_compare = sorted(lst_compare,key=lambda x:x[0])
    lst_compare.reverse()

    print("Start of command is probably at word number",lst_compare[0][1])
    print("Command part:"," ".join(string_words[lst_compare[0][1]:]))
    print("Callsign part:"," ".join(string_words[:lst_compare[0][1]]))

def parse_command_with_string_comparison(s):

    lst_compare = []

    for i in range(len(commands)):
        p = commands[i][3]
        ratio = similar(p,s)
        lst_compare.append([ratio,i])

    lst_compare = sorted(lst_compare, key=lambda x: x[0])
    lst_compare.reverse()

    print("Most similar command:",commands[lst_compare[0][1]])
    #print("Score:",lst_compare[0][0])

    # detect start of command

    most_sim_command = commands[lst_compare[0][1]][3]

    lst_compare = []

    string_words = s.split(" ")
    for i in range(len(string_words)):
        cut = " ".join(string_words[i:])
        similarity = similar(most_sim_command,cut)
        lst_compare.append([similarity,i])

    lst_compare = sorted(lst_compare,key=lambda x:x[0])
    lst_compare.reverse()

    command_part = " ".join(string_words[lst_compare[0][1]:])
    callsign_part = " ".join(string_words[:lst_compare[0][1]])

    # parse command and callsign

    command_part = parse_number_errors(command_part)
    callsign_part = parse_number_errors(callsign_part)

    print("Start of command is probably at word number",lst_compare[0][1])
    print("Command part:",command_part)
    print("Callsign part:",callsign_part)

    




a = AudioRecognizer()
a.start()

# get most similar command

#s = "air mexico 225 to clear for the aisle S roach runway 25"
