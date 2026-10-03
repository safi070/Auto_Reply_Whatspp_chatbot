#pip install pyautogui
#pip install pyperclippip
#pip install groq  (--)



import pyautogui
import time
import pyperclip

pyautogui.click(1268, 1039)
time.sleep(0.5)

# Move to starting point
pyautogui.moveTo(1814, 917, duration=0.3)

# Hold left mouse button
pyautogui.mouseDown(button="left")
time.sleep(0.3)

# Drag to the other corner
pyautogui.moveTo(679, 206, duration=1.5)

# Release
pyautogui.mouseUp(button="left")
# Copy
pyautogui.hotkey("ctrl", "c")
time.sleep(1)

pyautogui.click(684, 200)
time.sleep(0.5)

# came back to VS code 
# pyautogui.click(1268, 1039)
# time.sleep(0.5)

text= pyperclip.paste( )
print(text)

