from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    STACKEXCHANGE_KEY: str
    STACKEXCHANGE_BASE_URL: str = "https://api.stackexchange.com/2.3"
    STACKEXCHANGE_SITE: str = "stackoverflow"
    REDIS_URL: str = "redis://localhost:6380"
    MAX_CONCURRENCY: int = 10
    
    PAGE_SIZE: int = 15
    REQUEST_TIMEOUT: int = 25
    TTL: int = 3600
    RETRY_ATTEMPTS: int = 3
    RETRY_WAIT: int = 1

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings() 
