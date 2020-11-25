#adapted by regEx from altf4's project https://github.com/altf4/libmelee
import signal
import sys
import os
import melee

path = None
port = 51441
volume = 70
menu = False

#simple parser for the config file
configPath = melee.console.get_slippiMusic_config_path()
try:
    configFile = open(configPath)
except FileNotFoundError:
    print("No config file found at " + configPath + "! Using defaults...")
else:
    for line in configFile:
        split = line.split("=")
        var = split[0].strip().lower()
        if var == "path":
            path = split[1].strip()
        elif var == "slippi_port":
            try:
                port = int(split[1].strip())
            except valueError:
                input('There was an error parsing the port in the config file! Should be "slippi_port = [num]. Pres enter to exit...')
                sys.exit(-1)
        elif var == "volume":
            try:
                volume = int(split[1].strip())
                if volume > 100:
                    volume = 100
                elif volume < 0:
                    volume = 0
            except valueError:
                input('There was an error parsing the volume in the config file! Should be "volume = [num]! Press enter to exit...')
                sys.exit(-1)
        elif var == "menu":
            menu = split[1].strip().lower()[0] in ["y", "t"]
    

console = melee.Console(path=path,
                        slippi_port=port,
                         volume = volume, menu = menu)
                        
# This isn't necessary, but makes it so that Dolphin will get killed when you ^C
def signal_handler(sig, frame):
    console.stop()
    print("Shutting down cleanly...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Run the console
if(path):
    console.run()

# Connect to the console
while True:
    print("Connecting to console...")
    if console.connect():
        print("Connected to console!")
        break
    user_input = input("ERROR: Failed to connect to the console. Try again? y/n ")
    if(str(user_input).strip()[0] != 'y'):    
        sys.exit(-1)
    
    
while True:
    console.step();
