from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "1235"
    POSTGRES_DB: str = "llm_db"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    GEMINI_API_KEY: str = "mock-key"

    class Config:
        env_file = ".env"

settings = Settings()
