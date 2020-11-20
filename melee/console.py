"""The Console represents the engine running the game.
This can be Dolphin (Slippi's Ishiiruka) or an SLP file. The Console object
is your method to start and stop Dolphin, set configs, and get the latest GameState.
"""
#Adapted by regEx from altf4's libmelee project https://github.com/altf4/libmelee
from collections import defaultdict

import time
import threading
import os
import configparser
import subprocess
import platform
import base64
import sys
from pygame import mixer
from pygame import error as pg_error
import numpy as np

from melee.slippstream import SlippstreamClient, CommType, EventType


class SlippiVersionTooLow(Exception):
    """Raised when the Slippi version is not recent enough"""
    def __init__(self, message):
        self.message = message

#Gets the config file's path, which doesn't work in slippiMusic.py for some reason
def get_slippiMusic_config_path():
    return os.path.join(os.path.dirname(__file__), 'config.txt')

def execute_and_quit(command, env):
    if platform.system() == "Darwin": #mac
        command.insert(0, "open") #can't run directly on mac, gotta call open on it
        command.append("-W") #tells thread to wait until program exits
    try:
        process = subprocess.Popen(command, env=env)
        process.wait()
        print("Dolphin closed! exiting...")
        os._exit(0)
    except PermissionError:
        print("Access denied to your Dolphin executable! Can't open Dolphin automatically")
    except FileNotFoundError:
        print("Path to your Dolphin executable is incorrect! Can't open Dolphin automatically")

# pylint: disable=too-many-instance-attributes
class Console:
    """The console object that represents your Dolphin / Wii / SLP file
    """
    def __init__(self,
                 path=None,
                 is_dolphin=True,
                 slippi_address="127.0.0.1",
                 slippi_port=51441,
                 volume = 70,
                 menu = False):
        """Create a Console object
        Args:
            path (str): Path to the directory where your dolphin executable is located.
                If None, will assume the dolphin is remote and won't try to configure it.
            slippi_address (str): IP address of the Dolphin / Wii to connect to.
            slippi_port (int): UDP port that slippi will listen on
            volume (int) the volume music should play at, between 0 and 100
            menu (boolean) True if you want menu music to play, false otherwise. 
        """
        self.is_dolphin = is_dolphin
        self.path = path
        self.slippi_address = slippi_address
        """(str): IP address of the Dolphin / Wii to connect to."""
        self.slippi_port = slippi_port
        """(int): UDP port of slippi server. Default 51441"""
        self.eventsize = [0] * 0x100
        self.cursor = 0
        self._frame = 0
        """(str): The SLP version this stream/file currently is."""
        self._use_manual_bookends = False
        #self._costumes = {0:0, 1:0, 2:0, 3:0}
        #self._cpu_level = {0:0, 1:0, 2:0, 3:0}
        self._process = None
        try:
            mixer.init()
        except pg_error:
            print("Failed to initialize the mixer! Check that your audio devices are working properly")
        #self.volume = volume
        else:
            mixer.music.set_volume(volume/100.0)
        
        self.menu = menu
        
        self.fileNames = [None]*33
        configPath = os.path.normpath(os.path.join(os.path.dirname(__file__), 'music/musicConfig.txt'))
        try:
            configFile = open(configPath)
        except FileNotFoundError:
            input("No music config file found at " + configPath + "! Press enter to exit...")
            sys.exit(1)
        else:
            for line in configFile:
                split = line.split(":")
                try:
                    stageID = int(split[0])
                    if(stageID > 32):
                        continue #skip invalid
                    self.fileNames[stageID] = split[1].rstrip()
                except ValueError:
                    continue
        self._slippstream = SlippstreamClient(self.slippi_address, self.slippi_port)        
        if self.is_dolphin:
            self._slippstream = SlippstreamClient(self.slippi_address, self.slippi_port)
            if self.path:
                # Setup some dolphin config options
                dolphin_config_path = self._get_dolphin_config_path() + "Dolphin.ini"
                config = configparser.SafeConfigParser()
                config.read(dolphin_config_path)
                try:
                    self.slippi_port = int(config["Core"]["slippispectatorlocalport"])
                    if(not config["Core"]["slippienablespectator"]): #this needs to be true in order for this to connect to slippi
                        config.set("Core", 'slippienablespectator', "True")
                        try:
                            with open(dolphin_config_path, 'w') as dolphinfile:
                                config.write(dolphinfile)
                        except PermissionError:
                            print("Access denied to your Dolphin.ini file at " + dolphin_config_path + "! Means I can't automatically configure Dolphin. Run as administrator or make open that config file and make sure that \"slippienablespectator\" is set to True.")
                except (configparser.NoSectionError, KeyError):
                    print("Invalid Dolphin.ini file! Usually means your Dolphin path is wrong.")
        #else:
            #self._slippstream = SLPFileStreamer(self.path)  

    def connect(self):
        """ Connects to the Slippi server (dolphin or wii).
        Returns:
            True is successful, False otherwise
        """
        to_return = self._slippstream.connect()
        if(to_return):
            if(self.menu):
                self.playMusic("menu.mp3")
        return to_return


    def run(self, iso_path=None, dolphin_config_path=None, environment_vars=None):
        """Run the Dolphin emulator.
        This starts the Dolphin process, so don't run this if you're connecting to an
        already running Dolphin instance.
        Args:
            iso_path (str, optional): Path to Melee ISO for dolphin to read
            dolphin_config_path (str, optional): Alternative config path for dolphin
                if not using the default
            environment_vars (dict, optional): Dict (string->string) of environment variables to set
        """
        if self.is_dolphin and self.path:
            exe_name = "dolphin-emu"
            if platform.system() == "Windows":
                exe_name = "Dolphin.exe"
            elif platform.system() == "Darwin":
                exe_name = "Slippi Dolphin.app"

            exe_path = ""
            if self.path:
                exe_path = self.path
            command = [exe_path + "/" + exe_name]
            if platform.system() == "Linux" and os.path.isfile(self.path):
                command = [self.path]
            if iso_path is not None:
                command.append("-e")
                command.append(iso_path)
            if dolphin_config_path is not None:
                command.append("-u")
                command.append(dolphin_config_path)
            env = os.environ.copy()
            if environment_vars is not None:
                for var, value in environment_vars.items():
                    env[var] = value
            t = threading.Thread(target = execute_and_quit, args = [command, env], daemon = True)
            t.start()                

    def stop(self):
        """ Stop the console.
        For Dolphin instances, this will kill the dolphin process.
        For Wiis and SLP files, it just shuts down our connection
         """
        if self.path:
            self._slippstream.shutdown()
            # If dolphin, kill the process
            if self._process is not None:
                self._process.terminate()



    def step(self):
        """ 'step' to the next state of the game and flushes all controllers
        Returns:
            GameState object that represents new current state of the game"""
        frame_ended = False
        while not frame_ended:
            message = self._slippstream.dispatch()
            if message:
                if message["type"] == "game_event":
                    if len(message["payload"]) > 0:
                        if self.is_dolphin:
                            frame_ended = self.__handle_slippstream_events(base64.b64decode(message["payload"]))
                        else:
                            frame_ended = self.__handle_slippstream_events(message["payload"])
                elif self._use_manual_bookends and message["type"] == "frame_end" and self._frame != -10000:
                    frame_ended = True
            else:
                return None
        return None
        """gamestate = self._temp_gamestate
        self._temp_gamestate = None
        self.__fixframeindexing(gamestate)
        self.__fixiasa(gamestate)
        # Start the processing timer now that we're done reading messages
        self._frametimestamp = time.time()
        return gamestate"""

    def __handle_slippstream_events(self, event_bytes):
        """ Handle a series of events, provided sequentially in a byte array """
        #gamestate.menu_state = enums.Menu.IN_GAME
        while len(event_bytes) > 0:
            event_size = self.eventsize[event_bytes[0]]
            if len(event_bytes) < event_size:
                print("WARNING: Something went wrong unpacking events. Data is probably missing")
                print("\tDidn't have enough data for event")
                return False
            if EventType(event_bytes[0]) == EventType.PAYLOADS:
                cursor = 0x2
                payload_size = event_bytes[1]
                num_commands = (payload_size - 1) // 3
                for i in range(0, num_commands):
                    command = np.ndarray((1,), ">B", event_bytes, cursor)[0]
                    command_len = np.ndarray((1,), ">H", event_bytes, cursor + 0x1)[0]
                    self.eventsize[command] = command_len+1
                    cursor += 3
                event_bytes = event_bytes[payload_size + 1:]

            elif EventType(event_bytes[0]) == EventType.FRAME_START:
                event_bytes = event_bytes[event_size:]

            elif EventType(event_bytes[0]) == EventType.GAME_START:
                #self.__game_start(gamestate, event_bytes)
                print("Game start")
                stage = np.ndarray((1,), ">H", event_bytes, 0x13)[0]
                print(stage)
                if(self.fileNames[stage] != None):
                    self.playMusic(self.fileNames[stage])
                else:
                    mixer.music.stop()
                event_bytes = event_bytes[event_size:]

            elif EventType(event_bytes[0]) == EventType.GAME_END:
                event_bytes = event_bytes[event_size:]
                print("Game end")
                if(self.menu):
                    self.playMusic("menu.mp3")
                else:
                    mixer.music.stop()
                return self._use_manual_bookends

            elif(EventType(event_bytes[0]) in [EventType.PRE_FRAME, EventType.POST_FRAME, EventType.GECKO_CODES, EventType.ITEM_UPDATE]):
                event_bytes = event_bytes[event_size:]
                
            elif EventType(event_bytes[0]) == EventType.FRAME_BOOKEND:
                #self.__frame_bookend(gamestate, event_bytes)
                event_bytes = event_bytes[event_size:]
                # If this is an old frame, then don't return it.
                #if gamestate.frame <= self._frame:
                    #return False
                #self._frame = gamestate.frame
                return True


            else:
                print("WARNING: Something went wrong unpacking events. " + \
                    "Data is probably missing")
                print("\tGot invalid event type: ", event_bytes[0])
                return False
        return False

    def playMusic(self, fileName):
        try:
            #print(os.path.dirname(__file__))
            dirname = os.path.dirname(__file__)
            musicPath = os.path.normpath(os.path.join(dirname, 'music/' + fileName))
            print(musicPath)
            mixer.music.stop()
            mixer.music.load(musicPath)
            mixer.music.play(-1)
        except pg_error:
            print("Couldn't play the media. Usually means the filename is wrong.")        

    def _get_dolphin_config_path(self):
        """ Return the path to dolphin's config directory
        (which is not necessarily the same as the home path)"""
        if self.path:
            if platform.system() == "Linux":
                # First check if the config path is here in the same directory
                if os.path.isdir(self.path + "/User/Config/"):
                    return self.path + "/User/Config/"
                # Otherwise, this must be an appimage install. Use the .config
                return str(Path.home()) + "/.config/SlippiOnline/Config/"
            elif platform.system() == "Darwin": #mac
                return os.path.join(self.path, "Slippi Dolphin.app/Contents/Resources/User/Config/")
            return self.path + "/User/Config/"


 
