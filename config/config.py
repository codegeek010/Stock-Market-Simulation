from pydantic_settings import BaseSettings


class DevelopConfig(BaseSettings):
    DATABASE_URL: str
    TEST_DATABASE_URL: str
    REDIS_URL: str
    KAFKA_BROKER: str
    SENTRY_DSN: str
    ACCESS_TOKEN_EXPIRE_MINUTES: str
    JWT_SECRET: str
    ALGORITHM: str

    class Config:
        env_file = ".env"
        from_attribute = True


settings = DevelopConfig()
