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

# Release and deploy
We run on Fly.io. See `.github/workflows/deploy.yml` for release and deploy trigger on each push to `main`

## Rolling back (oops)
- `fly releases --image`
- `fly deploy -i <image-name>`
- As per [here](https://community.fly.io/t/how-to-do-rollback-releases-3-different-ways/16347).

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
