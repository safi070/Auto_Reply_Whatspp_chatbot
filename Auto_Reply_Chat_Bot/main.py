"""
Spike - WhatsApp auto-responder using Groq + pyautogui/pyperclip

Watches one open WhatsApp chat window, waits for a NEW incoming message from
the other person, generates a reply with Groq (persona: "Spike"), then pastes
it into the input box and presses Enter.

Before running:
- Calibrate every pyautogui coordinate below to your own screen/window layout
  (use `pyautogui.position()` in a quick script to find exact pixel points).
- Keep WhatsApp open and the chat visible/active the whole time this runs.
- A quick heads-up: automating message sends this way sits outside WhatsApp's
  normal terms of use, and if the other side doesn't know they're talking to
  a bot that's worth being upfront about. Fine for a personal experiment with
  someone who's in on it - just don't point this at group chats or use it to
  contact people who haven't agreed to it.
"""

import os
import time
import pyautogui
import pyperclip
from groq import Groq

# ---------------- Config ----------------

GROQ_API_KEY = ("API_KEY") #put an API key I am entering it as it may get exhaust in github
MODEL = "openai/gpt-oss-120b"
POLL_INTERVAL = 3          # seconds between checks for a new message
SEND_DELAY = 0.05          # small pause between paste and Enter

# Screen coordinates -- calibrate these for your own setup
CHAT_SELECT_START = (1814, 917)   # bottom-right corner of the message area
CHAT_SELECT_END = (679, 206)      # top-left corner of the message area
MESSAGE_INPUT_BOX = (1130, 920)    # click point for the text input field

SYSTEM_PROMPT = """
You are Spike, a real person from Pakistan. You're a software developer who
loves coding, and you also work as an email marketing and copywriting expert.
You chat casually and naturally like a real person over WhatsApp: short,
conversational replies, occasional Pakistani English/Urdu phrasing where it
fits naturally, no over-explaining, no AI disclaimers, no "as an AI" language.
Stay in character as Spike at all times.
"""

client = Groq(api_key=GROQ_API_KEY)


# ---------------- Chat I/O (low-level, isolated so the rest doesn't care how) ----------------

def get_chat_text() -> str:
    """Select the visible chat area and return the copied text."""
    pyautogui.moveTo(*CHAT_SELECT_START, duration=0.3)
    pyautogui.mouseDown(button="left")
    time.sleep(0.2)
    pyautogui.moveTo(*CHAT_SELECT_END, duration=0.8)
    pyautogui.mouseUp(button="left")
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.3)
    return pyperclip.paste()


def get_last_line(chat_text: str) -> str:
    lines = [line.strip() for line in chat_text.splitlines() if line.strip()]
    return lines[-1] if lines else ""


def send_message(text: str) -> None:
    pyautogui.click(*MESSAGE_INPUT_BOX)
    time.sleep(0.3)
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(SEND_DELAY)
    pyautogui.press("enter")


# ---------------- Reply generation (isolated, swappable model/persona) ----------------

def generate_reply(incoming_message: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": incoming_message},
        ],
    )
    return response.choices[0].message.content.strip()


# ---------------- Main loop ----------------

def main():
    last_seen = ""       # last raw line already reacted to
    last_bot_reply = ""  # what Spike last sent, so we never "reply" to ourselves

    print("Spike is watching the chat... (Ctrl+C to stop)")

    while True:
        try:
            chat_text = get_chat_text()
            last_line = get_last_line(chat_text)

            is_new_line = bool(last_line) and last_line != last_seen
            is_from_other_person = last_line != last_bot_reply

            if is_new_line and is_from_other_person:
                print(f"New message: {last_line}")
                reply = generate_reply(last_line)
                send_message(reply)
                print(f"Spike replied: {reply}")

                last_bot_reply = reply
                last_seen = reply  # after sending, this is the newest line on screen
            else:
                last_seen = last_line

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()