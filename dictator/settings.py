from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Required config
    BOT_TOKEN: str
    DB_PASSWORD: str
    OC_GRAPHQL_KEY: str
    PLAYER_LIST_PASSWORD: str

    # Optional config
    BOT_PREFIX: str = "-"
    DICTATOR_VERSION: str = "HEAD"

    ADMIN_ROLE_ID: int = 604284386556510209
    MOD_ROLE_ID: int = 578867113817800715
    GAME_MOD_ROLE_ID: int = 924570507767083029

    DB_HOST: str = "db.twohoursonelife.com"
    DB_DATABASE: str = "PROD_2HOL"
    DB_USER: str = "dictator"

    ACTION_LOG_CHANNEL_ID: int = 620375198251745282
    MOD_LOG_CHANNEL_ID: int = 607929812119453697
    ACCOUNT_LOG_CHANNEL_ID: int = 973930931456987206
    STATS_CHANNEL_ID: int = 744031336448393328
    OC_CHANNEL_ID: int = 948569156217892944
    EXP_CHANNEL_ID: int = 623147077269979166
    VET_CHANNEL_ID: int = 984934568454926417
    GENERAL_CHANNEL_ID: int = 423293333864054837

    OC_GRAPHQL_ENDPOINT: str = "https://api.opencollective.com/graphql/v2"

    # Number of previous months to analyse for future forecasting
    OC_ANALYSIS_PERIOD_MONTHS: int = 6

    # Day of the month to generate and send the forecast message
    OC_FORECAST_MONTH_DAY: int = 7

    SENTRY_DSN: str = "https://d273912626b930e863089cd16baff50f@o4508150301065216.ingest.us.sentry.io/4508430421262336"
    SENTRY_ENVIRONMENT: str = "production"

    MAIN_COLOUR: int = 0xFFBB35


config = Settings()
