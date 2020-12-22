# SlippiMusic
An application for playing music while playing with Rollback Netcode. Since music is read from the disc, it's incompatable with Slippi rollback and it isn't planned to be implemented any time in the forseeable future. 

# How to use:
- Download the release for your operating system. At this time, I only have a release for Windows and Linux, but the python script works on MacOS as well. [Here is a guide on how to run SlippiMusic using the source code](https://github.com/Noah-C-S/SlippiMusic/wiki/Running-From-Source), which is how you run the program on MacOS.
	- path: The full path to your dolphin executable. Something like "path = C:\Program Files\FM-Slippi\Dolphin.exe". This expects a .exe on Windows, a .App file on MacOS, and works with either an executable or the .AppImage on Linux.
	- slippi_port: The port number that Slippi will use. This is ignored if you provide a path; instead it will read the slippispectatorlocalport property your Dolphin.ini file to figure out the port number. This defaults to the Slippi default (51441) if neither this nor a valid Dolphin path is provided.
	- volume: 0 is mute, 100 is loudest
	- menu: True if you want the program to emulate menu music, False otherwise.
	- iso_path: The full path to your melee iso. When you launch SlippiMusic, it will automatically give this iso to Dolphin to launch 
- Put the music files in the melee/music folder. The program will emulate the "intro" and "looping" sections of melee's music if the musicConfig.txt file is set up with them, but the music files need to be cut *exactly* at the loop points. You can extract loop points from the Melee ISO.
	- You can just use the files from the ["melee/music"](https://github.com/Noah-C-S/SlippiMusic/tree/master/melee/music) folder in the repository, it contains menu music and all tracks from tournament-legal stages.
	- If the "intro" and "looping" emulation is causing you problems (like popping at the loop point), then you can use the old files [here](https://github.com/Noah-C-S/SlippiMusic/tree/d7e1732389a06be028cbd6a994bf52d03acf6894/melee/music). If you can't be bothered to cut new files at the loop points for your own songs, then just use songs that are greater than 8 minutes long and it should be fine.
- The file names are defined by the musicConfig.txt file in the format "stageID:intro-filename:loop-filename" where the stageID is the internal id for each stage. If you provide one filename, then it will just loop that file, otherwise it will play "intro-filename" once and then loop "loop-filename" forever. For the menu music, replace the stageID with "menu". You can have multiple entries per stage, and you can control the relative probability of each song by making multiple entries for a single song (e.g. 2 entries for song A and 1 for song B means that song A will play 2/3 times on that stage) [The stage IDs are listed here.](https://www.ssbwiki.com/Debug_menu_(SSBM)#stages)
- Then just run the executable and it should work as long as it's set up properly, or output an error if it's not. Play a game or two in single player mode to test it out.

# Notes
- If you provide a path for the Dolphin executable, SlippiMusic will launch the game for you, and upon quitting Dolphin completely, SlippiMusic will exit automatically. You also need the "slippienablespectator" property set to True in your Dolphin.ini file; if it is false and you provided a path, SlippiMusic will attempt to set it to True and will log if it fails.
- If you do not provide a path, the program can still connect to a running instance of Dolphin.
- Sometimes it takes a moment for Dolphin to start up completely, so it doesn't always connect on the first try. You can tell it to retry easily from the command line.
- If a command line window launches and immediately closes, that means the program encountered an unhandled error. Unfortunately, you'll have to run it in the command line to see what it is.
- This program was adapted from some of the code in the [libmelee project](https://github.com/altf4/libmelee/) and is thus released under the GNU Lesser General Public License v3.
