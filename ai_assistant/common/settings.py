from dotenv import load_dotenv
from pydantic import PostgresDsn
from pydantic import SecretStr
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

load_dotenv()


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    APP_NAME: str = 'ai_assistant'
    ENVIRONMENT: str = 'development'
    LOGGING_LEVEL: str = 'INFO'
    JWT_SECRET: SecretStr = SecretStr('pass')
    GOOGLE_CLOUD_PROJECT: str = '<GOOGLE_CLOUD_PROJECT>'
    GOOGLE_CLOUD_LOCATION: str = '<GOOGLE_CLOUD_LOCATION>'
    GOOGLE_GENAI_USE_VERTEXAI: bool = True
    DEFAULT_MODEL: str = 'gemini-2.5-flash'

    DATABASE_HOST: str = 'localhost'
    DATABASE_NAME: str = 'ai_assistant'
    DATABASE_USER: str = 'postgres'
    DATABASE_PASSWORD: SecretStr = SecretStr('postgres')
    DATABASE_PORT: int = 5432

    LANGFUSE_HOST: str = 'https://cloud.langfuse.com'
    LANGFUSE_SECRET_KEY: SecretStr = SecretStr('langfuse_secret_key')
    LANGFUSE_PUBLIC_KEY: SecretStr = SecretStr('langfuse_public_key')
    LANGFUSE_DEBUG: bool = False

    @property
    def DATABASE_URL(self) -> PostgresDsn:  # noqa: N802
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            username=self.DATABASE_USER,
            password=self.DATABASE_PASSWORD.get_secret_value(),
            host=self.DATABASE_HOST,
            port=self.DATABASE_PORT,
            path=self.DATABASE_NAME,
        )


settings = AppSettings()
