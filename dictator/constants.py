import os

from dotenv import load_dotenv

load_dotenv()

# TODO: Refresh. Avoid declaring in global space to avoid testing needing to stub.

# Required environment variables
BOT_TOKEN = os.environ["BOT_TOKEN"]
DB_PASSWORD = os.environ["DB_PASS"]
OC_GRAPHQL_KEY = os.environ["OC_GRAPHQL_KEY"]
PLAYER_LIST_PASSWORD = os.environ["PLAYER_LIST_PASSWORD"]

# Optional environment variables, setting defaults
BOT_PREFIX = os.environ.get("BOT_PREFIX", "-")
DICTATOR_VERSION = os.environ.get("DICTATOR_VERSION", "HEAD")

ADMIN_ROLE_ID = int(os.environ.get("ADMIN_ROLE_ID", 604284386556510209))
MOD_ROLE_ID = int(os.environ.get("MOD_ROLE_ID", 578867113817800715))
GAME_MOD_ROLE_ID = int(os.environ.get("GAME_MOD_ROLE_ID", 924570507767083029))

DB_HOST = os.environ.get("DB_HOST", "db.twohoursonelife.com")
DB_DATABASE = os.environ.get("DB_DB", "PROD_2HOL")
DB_USER = os.environ.get("DB_USER", "dictator")

ACTION_LOG_CHANNEL_ID = int(os.environ.get("ACTION_LOG_CHANNEL_ID", 620375198251745282))
ACCOUNT_LOG_CHANNEL_ID = int(
    os.environ.get("ACCOUNT_LOG_CHANNEL_ID", 973930931456987206)
)
STATS_CHANNEL_ID = int(os.environ.get("STATS_CHANNEL_ID", 744031336448393328))
OC_CHANNEL_ID = int(os.environ.get("OC_CHANNEL_ID", 948569156217892944))
EXP_CHANNEL_ID = int(os.environ.get("EXP_CHANNEL_ID", 623147077269979166))
VET_CHANNEL_ID = int(os.environ.get("VET_CHANNEL_ID", 984934568454926417))
GENERAL_CHANNEL_ID = int(
    os.environ.get("GENERAL_CHANNEL_ID", 423293333864054837)
)

OC_GRAPHQL_ENDPOINT = os.environ.get(
    "OC_GRAPHQL_ENDPOINT", "https://api.opencollective.com/graphql/v2"
)

# Number of previous months to analyse for future forecasting
OC_ANALYSIS_PERIOD_MONTHS = int(os.environ.get("OC_ANALYSIS_PERIOD_MONTHS", 6))

# Day of the month to generate and send the forecast message
OC_FORECAST_MONTH_DAY = int(os.environ.get("OC_FORECAST_MONTH_DAY", 7))

SENTRY_DSN = os.environ.get(
    "SENTRY_DSN",
    "https://d273912626b930e863089cd16baff50f@o4508150301065216.ingest.us.sentry.io/4508430421262336",
)
SENTRY_ENVIRONMENT = os.environ.get("SENTRY_ENVIRONMENT", "dev")

MAIN_COLOUR = 0xFFBB35
