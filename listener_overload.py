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
from pynput import keyboard

AudioSource = sr.AudioSource
AudioData = sr.AudioData

def listen(self, source: sr.AudioSource, timeout=None, phrase_time_limit=None, end_func=None):
    """Records a single phrase from 'source' into an 'AudioData' instance, which it returns."""
    
    assert isinstance(source, AudioSource), "Source must be an audio source"
    assert source.stream is not None, "Audio source must be entered before listening"
    assert self.pause_threshold >= self.non_speaking_duration >= 0

    seconds_per_buffer = float(source.CHUNK) / source.SAMPLE_RATE
    pause_buffer_count = int(math.ceil(self.pause_threshold / seconds_per_buffer))
    phrase_buffer_count = int(math.ceil(self.phrase_threshold / seconds_per_buffer))
    non_speaking_buffer_count = int(math.ceil(self.non_speaking_duration / seconds_per_buffer))

    elapsed_time = 0
    buffer = b""
    while True:
        frames = collections.deque()
        while True:
            elapsed_time += seconds_per_buffer

            if timeout and elapsed_time > timeout:
                raise sr.WaitTimeoutError("Listening timed out while waiting for phrase to start")

            buffer = source.stream.read(source.CHUNK)

            if len(buffer) == 0:
                break  # Reached end of the stream
            frames.append(buffer)

            # Ensure we only keep the needed amount of non-speaking buffers
            if len(frames) > non_speaking_buffer_count:
                frames.popleft()

            # Detect whether speaking has started on audio input
            energy = audioop.rms(buffer, source.SAMPLE_WIDTH)
            if energy > self.energy_threshold:
                break

            # Dynamically adjust the energy threshold
            if self.dynamic_energy_threshold:
                damping = self.dynamic_energy_adjustment_damping ** seconds_per_buffer
                target_energy = energy * self.dynamic_energy_ratio
                self.energy_threshold = self.energy_threshold * damping + target_energy * (1 - damping)

        # Read audio input until the phrase ends
        pause_count, phrase_count = 0, 0
        phrase_start_time = elapsed_time
        while True:
            elapsed_time += seconds_per_buffer
            if phrase_time_limit and elapsed_time - phrase_start_time > phrase_time_limit:
                break

            buffer = source.stream.read(source.CHUNK)
            if len(buffer) == 0:
                break  # Reached end of the stream
            if not key_pressed:  # If the key is released
                break  # Finish the loop
            frames.append(buffer)
            phrase_count += 1

            # Check if speaking has stopped for longer than the pause threshold
            energy = audioop.rms(buffer, source.SAMPLE_WIDTH)
            if energy > self.energy_threshold:
                pause_count = 0
            else:
                pause_count += 1
            if pause_count > pause_buffer_count:  # End of the phrase
                break

        # Check if the detected phrase is long enough
        phrase_count -= pause_count
        if not key_pressed:  # If the key is released
            break  # Finish the loop
        if phrase_count >= phrase_buffer_count or len(buffer) == 0:
            break  # Phrase is long enough or end of stream reached

    # Obtain frame data
    for i in range(pause_count - non_speaking_buffer_count):
        frames.pop()  # Remove extra non-speaking frames at the end
    frame_data = b"".join(frames)

    return AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
