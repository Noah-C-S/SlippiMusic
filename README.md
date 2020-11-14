# SlippiMusic
An application for playing music while playing with Rollback Netcode. Since music is read from the disc, it's incompatable with Slippi rollback and it isn't planned to be implemented any time in the forseeable future. 

# How to use:
- Download the release for your operating system. At this time, I only have a release for Windows, but you can try downloading the Python source code and running it on your operating system and it might work.
- Set up the config files and music. The melee/config.txt file has four options:
	- path: The full path to the folder containing your dolphin executable. Something like "path = C:\Program Files\FM-Slippi"
	- slippi_port: The port number that Slippi will use. This is ignored if you provide a path; instead it will read the slippispectatorlocalport property your Dolphin.ini file to figure out the port number. This defaults to the Slippi default (51441) if it isn't provided.
	- volume: 0 is mute, 100 is loudest
	- menu: True if you want the program to emulate menu music, False otherwise.
- Put the music files in the melee/music folder. The program doesn't emulate the "intro" and "looping" sections of Melee's music, so while it will loop whatever music you play, they don't loop very well, so it's best if these are at least 8 minutes long.
	-You can just use the files from the "melee/music" folder in the repository
- The file names are defined by the musicConfig.txt file in the format "stageID:filename" where the stageID is the internal id for each stage. [They are listed here.](https://www.ssbwiki.com/Debug_menu_(SSBM)#stages)
- Then just run slippiMusic.exe and it should work as long as it's set up properly, or output an error if it's not. Play a game or two in single player mode to test it out.

# Notes
If you provide a path for the Dolphin executable, SlippiMusic will launch the game for you, and upon quitting Dolphin completely, SlippiMusic will exit automatically. You also need the "slippienablespectator" property set to True in your Dolphin.ini file; if it is false and you provided a path, SlippiMusic will attempt to set it to True and will log if it fails.  
If a command line window launches and immediately closes, that means the program encountered an unhandled error. Unfortunately, you'll have to run it in the command line to see what it is.  
This program was adapted from some code in the [libmelee project](https://github.com/altf4/libmelee/) and is thus released under the GNU Lesser General Puglic License v3. 