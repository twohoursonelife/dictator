# dictator

The Dictator of 2HOL. Taking care of displaying user and player information about Two Hours One Life in our Discord guild.

## Features

- Users must read and acknowledge rules in our Discord to access the rest of the guild.

- Upon acknowledging the rules, a user is generated a game account consisting of a username and key. They are sent this information along with information on how to play for the first time.

- Ability for players to be sent their key again in case they lose the original message.

- Displays players online statistic in general channel topic and logs to a file with a timestamp for later graphing.

- Admins can ban, unban, search player lives and view information about game accounts.

## Commands

Commands must begin with the configured prefix. By default this is `-` (hyphen).

| Command | Usage | Purpose | Required Role |
|--|--|--|--|
| help | help [command] | Display information about all commands in Discord. Optionally display help about a specific command. |  Everyone  |
| key | key | Sends game account details to user in case they lose the original message. |  Everyone  |
| ping | ping | Pong! Check the bot is responding and see the latency. |  Everyone  |
| rtfm | rtfm | "Read the 'fricken' manual". Sends a link to the first time playing manual in the current channel.  |  Everyone  |
| whowas | whowas \<charcter\> | Searches the life log for a specific character and displays their username and a death timestamp. |  Admin, Mod  |
| unban | unban \<user\> [reason]| Unbans the specified user from the game. Default reason is "It's your lucky day!". The user argument can be a Discord user tag, a Discord username with discriminator or a Discord user ID. |  Admin, Mod  |
| info | info \<user\> | Sends you infomation about a player. |  Everyone  |
| ban | ban \<user\> [reason] | Bans the specified user from the game. Default reason is "The ban hammer has spoken!". The user argument can be a Discord user tag, a Discord username with discriminator or a Discord user ID. |  Admin, Mod  |
| regenerate | regenerate \<user\> | Regenerate a users key. This should be used when a users account is leaked. |  Admin, Mod  |

## Setup guide to run the bot
*This guide is current as of the time of writing. Past and future versions of software may be compatible. This guide is written based upon usage on Ubuntu 18.04. There may be slight differences for other platforms. This guide also assumes the database and discord are setup as required.*


### Prequisited software
- Python >3.8.0
- Poetry >1.0.0

### Steps
1. Clone the repository and change into the directory
- `git clone https://github.com/twohoursonelife/dictator.git`
- `cd dictator`

2. Install dependencies
- `poetry install`

3. Enable the Poetry virtual environment
- `poetry shell`

4. Run the bot once, expect it to tell you an error and crash. This generates the default config.
- `python dictator/dictator.py`

5. Make the necessary configuration in the config file found relatively at `dictator/utility/config.ini`
Specifically, you will need to add the bot token, database details and ensure channel ID’s are correct. Save the file and ensure you return to the root directory of the repository.

6. Finally, run the bot.
- `python dictator/dictator.py`

You should now have the bot running. If you have any trouble or come across any errors, please open an issue and give as much information as you can about the problem you’re having.

I highly suggest to use a process manager to continually run the bot, such as Screen, Tmux, PM2 or alike.