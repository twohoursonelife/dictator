import os
from dotenv import load_dotenv

load_dotenv()

# Required environment variables
BOT_TOKEN = os.environ["BOT_TOKEN"]
DB_HOST = os.environ["DB_HOST"]
DB_DATABASE = os.environ["DB_DB"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASS"]
OC_GRAPHQL_KEY = os.environ["OC_GRAPHQL_KEY"]

# Optional environment variables, setting defaults
BOT_PREFIX = os.environ.get("BOT_PREFIX", "-")
LOG_CHANNEL_ID = int(os.environ.get("LOG_CHANNEL_ID", 620375198251745282))
DEBUG_CHANNEL_ID = int(os.environ.get("DEBUG_CHANNEL_ID", 973930931456987206))
STATS_CHANNEL_ID = int(os.environ.get("STATS_CHANNEL_ID", 744031336448393328))
OC_CHANNEL_ID = int(os.environ.get("OC_CHANNEL_ID", 948569156217892944))

OC_GRAPHQL_ENDPOINT = os.environ.get("OC_GRAPHQL_ENDPOINT", "https://api.opencollective.com/graphql/v2")

# Number of previous months to analyse for future forecasting
OC_ANALYSIS_PERIOD_MONTHS = int(os.environ.get("OC_ANALYSIS_PERIOD_MONTHS", 6))

# Day of the month to generate and send the forecast message
OC_FORECAST_MONTH_DAY = int(os.environ.get("OC_FORECAST_MONTH_DAY", 1))