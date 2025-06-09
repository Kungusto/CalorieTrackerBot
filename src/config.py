from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings): 

    @property
    def DB_URL(self): 
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    DB_PORT: int
    DB_HOST: str
    DB_USER: str
    DB_PASSWD: str
    DB_NAME: str

    API_TOKEN_TG: str
    API_KEY_GPT: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()