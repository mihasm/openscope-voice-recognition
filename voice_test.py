#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class

import speech_recognition as sr
import time

# obtain audio from the microphone
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Adjusting for ambient noise, be quiet!")
    time.sleep(1)
    r.adjust_for_ambient_noise(source)  # listen for 1 second to calibrate the energy threshold for ambient noise levels
    

    # recognize speech using Sphinx
    while True:
        print("Say something!")
        audio = r.listen(source)
        try:
            print("Sphinx thinks you said " + r.recognize_sphinx(audio))
        except sr.UnknownValueError:
            print("Sphinx could not understand audio")
        except sr.RequestError as e:
            print("Sphinx error; {0}".format(e))