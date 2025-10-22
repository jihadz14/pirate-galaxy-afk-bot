###################
# Made by Eclip5e #
###################
# Original Version - Unmodified

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.dont_write_bytecode = True

from src.bot.importer import Importer
Importer.verifyLibs({'pyautogui', 'keyboard', 'colorama', 'requests', 'pytesseract', 'opencv-python', 'pywin32'})

# Import Modules
from colorama import Fore, Back, Style
from src.bot import PGBot, BotState
from time import sleep, time
import colorama
import pyautogui
import json
import keyboard
import cv2 as cv
import numpy as np

# Load Settings
settings_path = os.path.join(os.path.dirname(__file__), 'config', 'settings.json')
with open(settings_path) as f:
    settings = json.load(f)

# Vars
version = '0.3.1'
appName = 'Pirate Galaxy Bot'

colorama.init()
bot = PGBot(settings, appName, version)

# Start Bot
bot.terminal(f'{appName} v{version}', 'info')
bot.terminal('Made by Eclip5e\n', 'info')
bot.terminal('Initializing...')

sleep(1)
bot.start()

# Main Loop
loop_time = time()
while(True):
    if not bot.paused:
        # Update bots targets
        bot.update_targets()

        # Show FPS
        #print('FPS {}'.format(1 / (time() - loop_time)))
        loop_time = time()

        # Print HP and Energy
        print(f'{Fore.GREEN}HP: {bot.plr_hp} | {Fore.LIGHTCYAN_EX}Energy: {bot.plr_energy}{Fore.WHITE}{bot.ws}', end='\r')
    else:
        sleep(0.2)

    # Hotkeys
    if keyboard.is_pressed('q'): # Quit
        bot.stop()
        cv.destroyAllWindows()
        break
    if keyboard.is_pressed('p'): # Pause
        if bot.paused:
            bot.paused = False
            print(f'{Fore.LIGHTCYAN_EX}Unpaused{Fore.WHITE}{bot.ws}', end='\r')
            sleep(1)
        else:
            bot.paused = True
            print(f'{Fore.LIGHTCYAN_EX}Paused{Fore.WHITE}{bot.ws}', end='\r')
            sleep(1)

# Quit Application
bot.terminal(f'\nQuit', 'danger')
