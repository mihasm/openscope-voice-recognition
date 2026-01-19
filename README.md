# OpenScope Voice Recognition

A voice recognition system for [OpenScope](https://github.com/openscope/openscope), an air traffic control simulation game. This tool converts spoken ATC (Air Traffic Control) commands into OpenScope command format and automatically inputs them into the game.

## Features

- **Push-to-talk interface**: Press and hold the Shift key to speak
- **Automatic command recognition**: Converts natural speech into OpenScope command format
- **Airline callsign recognition**: Recognizes airline names and converts them to ICAO codes
- **Phonetic alphabet support**: Handles NATO phonetic alphabet pronunciation
- **Number parsing**: Converts spoken numbers to digits
- **Automatic game integration**: Types commands directly into OpenScope

## Supported Commands

The system recognizes various ATC commands including:

- Heading assignments (`"turn left heading 180"`, `"fly heading 270"`)
- Altitude changes (`"climb and maintain flight level 350"`, `"descend and maintain flight level 180"`)
- Speed instructions (`"reduce speed to 250"`, `"set speed to 300"`)
- Clearance commands (`"cleared for takeoff"`, `"cleared as filed"`)
- Runway assignments (`"taxi to runway 27L"`, `"expect runway 09R"`)

## Installation

### Prerequisites

- Python 3.7+
- Internet connection (uses Google Speech Recognition API)
- OpenScope game running

### Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### System Dependencies

**macOS:**
```bash
brew install portaudio
```

**Ubuntu/Debian:**
```bash
sudo apt-get install python3-pyaudio portaudio19-dev
```

**Windows:**
Download and install PyAudio from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

## Usage

### Running the Voice Recognition System

1. **Start the voice recognition system:**
   ```bash
   python main.py
   ```

2. **In OpenScope:**
   - Make sure the command input field is active
   - Press and hold the **Shift key** to start speaking
   - Speak your ATC command clearly
   - Release the Shift key to send the command

### Testing with Examples

You can test the command parsing without voice input:

```bash
python example.py
```

This will show how various spoken commands are converted to OpenScope format.

### Voice Command Examples

- Say: *"Delta 123 turn left heading 270"*
- Say: *"American 456 climb and maintain flight level 350"*
- Say: *"United 789 taxi to runway 25R"*
- Say: *"Speedbird 123 descend and maintain flight level 180"*

## Configuration

The system uses the following data files:

- `airlines.json`: Airline callsign to ICAO code mappings
- `phonetic_icao.txt`: NATO phonetic alphabet mappings
- `phonetic_numbers.txt`: Number pronunciation mappings

These files are automatically loaded when the program starts.

## How It Works

1. **Speech Recognition**: Uses Google Speech Recognition API to convert audio to text
2. **Text Processing**: Parses the recognized text to identify callsign and command portions
3. **Phonetic Conversion**: Converts spoken phonetics to standard ICAO format
4. **Command Formatting**: Maps natural language to OpenScope command syntax
5. **Auto-Input**: Uses keyboard simulation to type commands into the game

## Troubleshooting

### Common Issues

**"Could not understand the audio"**
- Speak more clearly and closer to the microphone
- Reduce background noise
- Check microphone settings

**Commands not appearing in OpenScope**
- Make sure OpenScope is the active window
- Ensure the command input field is focused
- Check that pyperclip and pynput are working correctly

**Microphone not detected**
- Check microphone permissions
- Try a different microphone
- Restart the application

### Debug Mode

For troubleshooting, you can modify the code to add debug output by uncommenting print statements in `main.py`.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is not affiliated with OpenScope or any air traffic control organizations. It is intended for entertainment and educational purposes only.

## Shoutout

Thanks to openscope.co for the cool game!