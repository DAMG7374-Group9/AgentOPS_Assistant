from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings, extra="ignore"):
    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str
    AWS_S3_BUCKET: str

    # JWT Authentication
    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRATION_SECONDS: int = 60 * 60 * 3  # 3 hours
    JWT_REFRESH_TOKEN_EXPIRATION_SECONDS: int = 60 * 60 * 24 * 1  # 1 day
    JWT_ALGORITHM: str = "HS256"

    # Postgres
    POSTGRES_CONN_STRING: str
    POSTGRES_URI: str | None = None

    # Pinecone
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str
    PINECONE_INDEX_NAME: str

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_EMBEDDINGS_MODEL: str = "text-embedding-3-small"

    # Tavily
    TAVILY_API_KEY: str

    # Snowflake
    SNOWFLAKE_DB_USER: str
    SNOWFLAKE_DB_PASSWORD: str
    SNOWFLAKE_DB_ACCOUNT: str
    SNOWFLAKE_DB_DATABASE: str
    SNOWFLAKE_DB_WAREHOUSE: str
    SNOWFLAKE_DB_SCHEMA: str
    SNOWFLAKE_DB_ROLE: str
    SNOWFLAKE_URI: str | None = None

    # Fast API config
    APP_TITLE: str = "AgentOps - Transcription & Chat Service"
    APP_VERSION: str = "0.1"

    # Logging Config
    LOG_LEVEL: str = "INFO"
    LOG_FILE_PATH: str = "logs/app.log"
    LOG_MAX_BYTES: int = 2000000  # Default to 2MB
    LOG_BACKUP_COUNT: int = 10

    # Hugging Face
    HF_TOKEN: str

    model_config = SettingsConfigDict(env_file=".env")

    @model_validator(mode="after")
    def validator(cls, values: "Settings") -> "Settings":
        values.POSTGRES_URI = values.POSTGRES_CONN_STRING
        values.SNOWFLAKE_URI =  (
            f"snowflake://{values.SNOWFLAKE_DB_USER}:{values.SNOWFLAKE_DB_PASSWORD}@{values.SNOWFLAKE_DB_ACCOUNT}/"
            f"{values.SNOWFLAKE_DB_DATABASE}/{values.SNOWFLAKE_DB_SCHEMA}?warehouse={values.SNOWFLAKE_DB_WAREHOUSE}&role={values.SNOWFLAKE_DB_ROLE}"
        )

        return values


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
