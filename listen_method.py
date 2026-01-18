import math
import audioop
import collections
import speech_recognition as sr
from pynput import keyboard

AudioSource = sr.AudioSource
AudioData = sr.AudioData

# Include both left and right Shift keys
BUTTONS = {keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r}
key_pressed = False  # Global variable to track if the button is pressed

# Event handler for key press
def on_press(key):
    global key_pressed
    if key in BUTTONS:
        key_pressed = True

# Event handler for key release
def on_release(key):
    global key_pressed
    if key in BUTTONS:
        key_pressed = False

# Start the keyboard listener in a separate thread
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

class AudioRecognizer:
    """Handles the process of recognizing audio with button control."""
    
    def __init__(self, do_something_with_text):
        """Initialize the audio recognizer.

        Args:
            do_something_with_text (callable): Function to process recognized text.
        """
        self.do_something_with_text = do_something_with_text
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Adjust for ambient noise at startup
        with self.microphone as source:
            print("Adjusting for ambient noise, please wait...")
            self.recognizer.adjust_for_ambient_noise(source)
        print("Ready. Press and hold the Shift key to speak.")

    def start(self):
        """Start the recognition loop."""
        while True:
            if key_pressed:
                print("Key pressed, starting recognition...")
                audio = self.listen_until_key_release()
                if audio is not None:
                    try:
                        text = self.recognizer.recognize_google(audio)
                        print(f"Recognized: {text}")
                        self.do_something_with_text(text)
                    except sr.UnknownValueError:
                        print("Could not understand the audio")
                    except sr.RequestError as e:
                        print(f"Could not request results; {e}")
                else:
                    print("No audio captured.")
                print("Waiting for keypress...")

    def listen_until_key_release(self):
        """Listen to the microphone until the key is released.

        Returns:
            sr.AudioData: The recorded audio data.
        """
        with self.microphone as source:
            # Ensure the audio source is properly initialized
            self.recognizer.energy_threshold = 300  # You can adjust this value
            frames = []
            seconds_per_buffer = float(source.CHUNK) / source.SAMPLE_RATE

            # Adjust recognizer settings if necessary
            pause_buffer_count = int(math.ceil(self.recognizer.pause_threshold / seconds_per_buffer))
            non_speaking_buffer_count = int(math.ceil(self.recognizer.non_speaking_duration / seconds_per_buffer))
            pause_count = 0

            while key_pressed:
                buffer = source.stream.read(source.CHUNK)
                if len(buffer) == 0:
                    break  # End of stream
                frames.append(buffer)

                # Energy of the audio signal
                energy = audioop.rms(buffer, source.SAMPLE_WIDTH)
                if energy > self.recognizer.energy_threshold:
                    pause_count = 0
                else:
                    pause_count += 1
                if pause_count > pause_buffer_count:
                    # Detected a pause longer than the pause threshold
                    # break
                    pass

            if not frames:
                return None  # No audio was captured

            # Remove extra non-speaking frames at the end
            for _ in range(pause_count - non_speaking_buffer_count):
                if frames:
                    frames.pop()

            frame_data = b''.join(frames)
            return sr.AudioData(frame_data, source.SAMPLE_RATE, source.SAMPLE_WIDTH)

if __name__ == "__main__":
    # Replace the lambda function with any function you want to handle the recognized text
    recognizer = AudioRecognizer(lambda x: print(f"Processed Text: {x}"))
    recognizer.start()
