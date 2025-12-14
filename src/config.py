import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bot_token: str
    openai_api_key: str
    openai_base_url: str = "https://api.z.ai/api/coding/paas/v4"
    model_name: str = "glm-4.6"
    
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    model_config = {
        "protected_namespaces": ("settings_",),
        "env_file": ".env",
        "extra": "ignore"
    }
    
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"


settings = Settings()