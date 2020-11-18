# team-coconut
**The bot made by team coconut**
___
## Setup
Python 3.8 required

Navigate to the root folder
```
cd team-coconut
```
Make a file called config.py with the following template
```py
REIMU_TOKEN = 'Discord token for bot 1'
REIMU_PREFIX = 'Prefix for bot 1'

BCOM_TOKEN = 'Discord token for bot 2'
BCOM_PREFIX = 'Prefix for bot 2'

ASTRA_TOKEN = 'Discord token for bot 3'
ASTRA_PREFIX = 'Prefix for bot 3'

WHITELISTED_OWNERS = [] #list which contanins the discord ids of the owners as int
CORE_GUILD = 0 #guild id of the main server of the bot
TIMELIMIT = 15*60 #max duration of a call
```
### Pipenv Installation
Install pipenv
```
pip install pipenv
```
Activate environment
```
pipenv shell
```
Install packages
```
pipenv install 
```
Check if all packages are installed
```
pip list
```
Run the program
```
python main.py
```
___
## Overview
Our bot is like a phone in discord,
it has a command to relay messages between text channels
and voice between two voice channels

# Commands
## Connect
Connects the current channel to any other channel in any other server

Usage - **`<prefix>connect [channel mention or id]`**

Example - `r1connect 773739934217011210`

This example makes the bot relay messages between the 
current channel with the channel with id 773739934217011210
in any other server
## Disconnect
Disconnects the current channel from all other channel connections

Usage - **`<prefix>disconnect`**(no other parameters)
## Save
It saves the number as a name so that you can call that number via that name
**(like a phonebook)**

Usage - **`save [guild id you want to save] [name]`**

Example - `r1save 771721715725369344 Home`
## Call
It relays voice between two voice channels registered via the register command

Usage - **`<prefix>call [guild id or name]`**

Examples :=
- `r1call 771721715725369344`
- `r1call Home`
## EndCall
Ends the call
## Register
Registers the guild to be callable
**(you should be in a voice channel)**
## Log
Shows you the call log of the guild
## Ping
Shows the latency of the bot
## Source
Shows the source code of any command
**(owner only command)**
## GetMessage
Gets the message from any server via id or link

Usage - **`getmessage [message id or link] <channel id> <server id>`**

Alias - `getmsg`
# LICENSE
All projects will merged into our Code Jam repository, which uses the MIT license. Please make sure that if you add assets, the licenses of those assets are compatible with the MIT license.

Authors: [Killua-Zoldyck-007](https://github.com/Killua-Zoldyck-007), [Crambor](https://github.com/Crambor), [TheAnonyMouse1337](https://github.com/TheAnonyMouse1337)