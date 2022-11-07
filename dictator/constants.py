import os

# Required environment variables
BOT_TOKEN = os.environ["BOT_TOKEN"]
DB_HOST = os.environ["DB_HOST"]
DB_DATABASE = os.environ["DB_DB"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASS"]

# Optional environment variables, setting defaults
BOT_PREFIX = os.environ.get("BOT_PREFIX", "-")
LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", 620375198251745282))
DEBUG_CHANNEL_ID = int(os.environ.get("DEBUG_CHANNEL_ID", 973930931456987206))
STATS_CHANNEL_ID = int(os.environ.get("STATS_CHANNEL_ID", 744031336448393328))