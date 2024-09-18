"""Summary

Attributes:
    AudioData (TYPE): Description
    AudioSource (TYPE): Description
    BUTTON (str): Description
"""
import keyboard  # using module keyboard
import io
import os
import sys
import subprocess
import wave
import aifc
import math
import audioop
import collections
import json
import base64
import threading
import platform
import stat
import hashlib
import hmac
import time
import uuid
import re

from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

import speech_recognition as sr
AudioSource = sr.AudioSource
AudioData = sr.AudioData

BUTTON = "shift"


def listen(self, source: sr.AudioSource, timeout=None, phrase_time_limit=None):
    """Records a single phrase from 'source' into an 'AudioData' instance, which it returns.
    
    Overloads listen function from sr.Recognizer(), to implement custom button logic.
    
    This is done by:
        1. waiting until the audio has an energy above 'recognizer_instance.energy_threshold'
        (the user has started speaking),
        2. recording until it encounters 'recognizer_instance.pause_threshold' seconds of
        non-speaking or there is no more audio input.
    
        This operation will always complete within 'timeout + phrase_timeout' seconds
        if both are numbers, either by returning the audio data, or by raising a
        'speech_recognition.WaitTimeoutError' exception.
    
    
    Args:
        source (sr.AudioSource): Description
        timeout (None, optional): Maximum number of seconds that this will wait
            for a phrase to start before giving up 
            and throwing an 'speech_recognition.WaitTimeoutError' exception.
            If 'timeout' is 'None', there will be no wait timeout.
        phrase_time_limit (None, optional): Maximum number of seconds that this will allow a phrase to continue
            before stopping and returning the part of the phrase processed before
            the time limit was reached. The resulting audio will be the phrase
            cut off at the time limit. If 'phrase_timeout' is 'None', there will
            be no phrase time limit.
    
    Returns:
        sr.AudioData: Description
    
    Raises:
        WaitTimeoutError: Description
    
    Deleted Parameters:
        snowboy_configuration (None, optional): Description
    """

    assert isinstance(source, AudioSource), "Source must be an audio source"
    assert source.stream is not None, "Audio source must be entered before listening, see documentation for 'AudioSource'; are you using 'source' outside of a 'with' statement?"
    assert self.pause_threshold >= self.non_speaking_duration >= 0

    seconds_per_buffer = float(source.CHUNK) / source.SAMPLE_RATE
    pause_buffer_count = int(
        math.ceil(self.pause_threshold / seconds_per_buffer))
    phrase_buffer_count = int(
        math.ceil(self.phrase_threshold / seconds_per_buffer))
    non_speaking_buffer_count = int(
        math.ceil(self.non_speaking_duration / seconds_per_buffer))

    elapsed_time = 0
    buffer = b""
    while True:
        frames = collections.deque()
        while True:
            elapsed_time += seconds_per_buffer

            if timeout and elapsed_time > timeout:
                raise WaitTimeoutError(
                    "listening timed out while waiting for phrase to start")

            buffer = source.stream.read(source.CHUNK)

            if len(buffer) == 0:
                # reached end of the stream
                break
            frames.append(buffer)

            # ensure we only keep the needed amount of non-speaking buffers
            if len(frames) > non_speaking_buffer_count:
                frames.popleft()

            # detect whether speaking has started on audio input
            # energy of the audio signal
            energy = audioop.rms(buffer, source.SAMPLE_WIDTH)
            if energy > self.energy_threshold:
                break

            # dynamically adjust the energy threshold using asymmetric weighted average
            if self.dynamic_energy_threshold:
                # account for different chunk sizes and rates
                damping = self.dynamic_energy_adjustment_damping ** seconds_per_buffer
                target_energy = energy * self.dynamic_energy_ratio
                self.energy_threshold = self.energy_threshold * \
                    damping + target_energy * (1 - damping)

        # read audio input until the phrase ends
        pause_count, phrase_count = 0, 0
        phrase_start_time = elapsed_time
        while True:
            # handle phrase being too long by cutting off the audio
            elapsed_time += seconds_per_buffer
            if phrase_time_limit and elapsed_time - phrase_start_time > phrase_time_limit:
                break

            buffer = source.stream.read(source.CHUNK)
            if len(buffer) == 0:
                break  # reached end of the stream
            if not keyboard.is_pressed(BUTTON):  # if key is released
                # print('Break!')
                break  # finishing the loop
            frames.append(buffer)
            phrase_count += 1

            # check if speaking has stopped for longer than the pause threshold on the audio input
            # unit energy of the audio signal within the buffer
            energy = audioop.rms(buffer, source.SAMPLE_WIDTH)
            if energy > self.energy_threshold:
                pause_count = 0
            else:
                pause_count += 1
            if pause_count > pause_buffer_count:  # end of the phrase
                break

        # check how long the detected phrase is, and retry listening if the phrase is too short
        phrase_count -= pause_count  # exclude the buffers for the pause before the phrase
        if not keyboard.is_pressed(BUTTON):  # if key is released
            # print('Break!')
            break  # finishing the loop
        if phrase_count >= phrase_buffer_count or len(buffer) == 0:
            break  # phrase is long enough or we've reached the end of the stream, so stop listening

    # obtain frame data
    for i in range(pause_count - non_speaking_buffer_count):
        frames.pop()  # remove extra non-speaking frames at the end
    frame_data = b"".join(frames)

    return AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)

class AudioRecognizer:

    """Summary
    
    Attributes:
        do_something_with_text (TYPE): Description
    """
    
    def __init__(self,do_something_with_text):
        """Summary
        
        Args:
            do_something_with_text (TYPE): Description
        """
        self.do_something_with_text = do_something_with_text

    def start(self):
        """Summary
        """
        r = sr.Recognizer()
        r.listen = listen

        def set_pressed():
            """Summary
            """
            audio = r.listen(r,source)
            # recognize speech using Google Speech Recognition
            try:
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`
                text = r.recognize_google(audio)
                print(">>" + text)
                self.do_something_with_text(text)
                

            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

            print("Waiting for keypress...")

        with sr.Microphone() as source:
            print("Adjusting for ambient noise, be quiet!")
            r.adjust_for_ambient_noise(source)  # listen for 1 second to calibrate the energy threshold for ambient noise levels

            keyboard.add_hotkey(BUTTON,lambda: set_pressed())
            print("Waiting for keypress...")
            keyboard.wait()

if __name__ == "__main__":
    a = AudioRecognizer(lambda x: print(x))
    a.start()