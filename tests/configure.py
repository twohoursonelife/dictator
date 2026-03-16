import os

# Set dummy environment variables for tests before dictator.settings is imported
os.environ.setdefault("BOT_TOKEN", "test_token")
os.environ.setdefault("DB_PASSWORD", "test_password")
os.environ.setdefault("OC_GRAPHQL_KEY", "test_key")
os.environ.setdefault("PLAYER_LIST_PASSWORD", "test_password")
