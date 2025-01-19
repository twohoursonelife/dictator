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
- rtfm
- whowas
- whowasext
- unban
- ban
- info
- regenerate

# Development
You need:
- Database
- Discord guild
- Docker compose
- uv

## Running
- Copy `example.env` to `.env`, update values.
- Start or reload `docker compose up --build --force-recreate`
- Stop `docker compose kill && docker compose rm -f`

## Sync commands
1. `-sync`
2. Ctrl + R, reload Discord.
