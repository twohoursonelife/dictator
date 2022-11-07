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
| whowas | whowas \<charcter\> | Searches the life log for a specific character and displays their username and a death timestamp. |  Moderator  |
| unban | unban \<user\> [reason]| Unbans the specified user from the game. Default reason is "It's your lucky day!". The user argument can be a Discord user tag, a Discord username with discriminator or a Discord user ID. |  Moderator  |
| info | info \<user\> | Sends you infomation about a player. |  Everyone  |
| ban | ban \<user\> [reason] | Bans the specified user from the game. Default reason is "The ban hammer has spoken!". The user argument can be a Discord user tag, a Discord username with discriminator or a Discord user ID. |  Moderator  |
| regenerate | regenerate \<user\> | Regenerate a users key. This should be used when a users account is leaked. |  Moderator  |

## Setup guide to run the bot
*This guide assumes the database and discord are setup as required.*

### Steps
1. Clone the repository and change into the directory.
- `git clone https://github.com/twohoursonelife/dictator.git`
- `cd dictator`

2. Install dependencies.
- `pipenv install`

1. Enable the virtual environment.
- `pipenv shell`

4. Copy `example.env` to `.env`, set required environment variables and optional variables if necessary.
- `cp example.env .env`
- [More info](#environment-variables)


5. Run the bot.
- `python dictator/dictator.py`

The bot should now be running.
It's best to use a process manager such as Screen, Tmux or PM2 to continually run the bot.

## Environment variables
See `example.env`

You can copy and rename this file to `.env` to easily set environment variables.