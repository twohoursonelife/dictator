# dictator

The Dictator of 2HOL. Taking care of displaying user and player information about Two Hours One Life in our Discord guild

## Features

- Generates a new Discord guild member their game access key when they pass the Discord onboarding (Selecting roles, channels, agreeing to rules)
- Members can access their game access key
- Members can view game stats of individual players
- Generates financial forecast based upon [our Open Collective](https://opencollective.com/twohoursonelife)
- Displays current living population in game
- Mods can see which member was a specific character in game
- Mods can ban and unban members from the game
- Mods can regenerate a members game access key

## Commands

Commands must begin with the configured prefix. By default this is `-` (hyphen)

- help
- key
- ping
- version
- rtfm
- whowas
- unban
- ban
- info
- regenerate

## Setup guide to run the bot
*This guide assumes the database and discord are setup as required*

### Steps
1. Clone the repository and change into the directory
- `git clone https://github.com/twohoursonelife/dictator.git`
- `cd dictator` 

2. Copy `example.env` to `.env`, set required environment variables and optional variables if necessary
- `cp example.env .env`
- [More info](#environment-variables)

3. Run the bot
- `docker compose up -d --pull always`

or for local development
- `pipenv sync`
- `pipenv shell`
- `python run dictator/dictator.py`

The bot should now be running

## Environment variables
See `example.env`

You can copy and rename this file to `.env` to easily set environment variables
