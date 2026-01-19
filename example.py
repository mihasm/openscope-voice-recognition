#!/usr/bin/env python3
"""Example usage of OpenScope Voice Recognition System

This script demonstrates how to use the voice recognition components
programmatically without the push-to-talk interface.
"""

from main import parse_voice

def main():
    """Demonstrate voice command parsing with example inputs."""

    # Example voice commands
    test_commands = [
        "delta 225 turn left heading 180",
        "american 456 climb and maintain flight level 350",
        "united 789 taxi to runway 25 right",
        "speedbird 123 descend and maintain flight level 180",
        "cleared for takeoff",
        "fly heading 090"
    ]

    print("OpenScope Voice Recognition - Example Usage")
    print("=" * 50)

    for command in test_commands:
        print(f"\nInput: '{command}'")
        try:
            result = parse_voice(command)
            print(f"Output: {result}")
        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 50)
    print("To use with actual voice input, run: python main.py")
    print("Press and hold Shift key to speak, then release to process.")

if __name__ == "__main__":
    main()