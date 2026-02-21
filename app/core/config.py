from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    APP_NAME: str = "mcmafia"
    BACKEND_PORT: int = 8000

    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_API_VERSION: str
    AZURE_OPENAI_DEPLOYMENT: str
    AZURE_EMBEDDING_DEPLOYMENT: str
    AZURE_EMBEDDING_ENDPOINT: str
    AZURE_EMBEDDING_API_KEY: str
    AZURE_EMBEDDING_API_VERSION: str

    LLAMA_PARSE_API_KEY: str

    MONGO_URI: str
    MONGO_DB_NAME: str

    QDRANT_URL: str
    QDRANT_API_KEY: str

    ELASTIC_ENDPOINT: str
    ELASTIC_API_KEY: str
    TAVILY_API_KEY: str


settings = Settings()
