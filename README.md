# SteamNonStaticIPUpdater

If you have a server with a non-static ip address but a hostname and you want to store this server into your Steam-favorites you need to update the server ip address manually everytime the server ip address has changed. This python-script will update the ip address in the Steam-Server file automatically.

HowTo set-up the script

1. on windows execute the run.bat script / on linux execute the run.sh script
2. paste the file path to the serverbrowser_hist.vdf file (for example: \Steam\userdata\25660381\7\remote\)


HowTo add a server to the auto-update list:

1. start the script by using run.bat or run.sh
2. use the "create" command
3. choose a server name
4. enter the server hostname
5. enter the query-port of the server (typically 27015)
6. start steam to verify that it worked (you may have to fully restart Steam a few times before the Server shown up)


HowTo update the server-ips

Possibility 1: execute update.bat or update.sh respectively
Possibility 2: start the main.py and use the "update command"
Possibility 3: start the main.py with the additional argument --update or -u

!Note: Steam needs to be turned off to execute the server-ip update!


HowTo delete a server from the auto-update list

1. start the script by using run.bat or run.sh
2. use the "delete" command
3. enter the name of the server you want to delete
4. confirm delete


All possible Commands:
- create
- delete
- update
- exit 

All possible optional Arguments
- -u, --update
- -r, --reset
- -h, --help

Requirements:

Python 3.7
vdf 3.2 

