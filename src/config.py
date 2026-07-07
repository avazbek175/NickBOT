from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
import os


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    bot_token: str
    admin_ids: str = ""
    bot_name: str = "NickForge AI"
    bot_description: str = "Professional Nickname Generator"
    bot_lang: str = "uz"

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "nickforge"
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_ssl_mode: str = "disable"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None

    force_join_enabled: bool = True
    referral_enabled: bool = True
    daily_bonus_enabled: bool = True
    daily_bonus_coins: int = 50
    referral_coins: int = 100

    log_level: str = "INFO"
    maintenance_mode: bool = False

    vercel_url: Optional[str] = None
    vercel_env: Optional[str] = None

    @property
    def admin_id_list(self) -> List[int]:
        ids = []
        for item in self.admin_ids.split(","):
            item = item.strip()
            if item.isdigit():
                ids.append(int(item))
        return ids

    @property
    def database_url(self) -> str:
        url = f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        if self.db_ssl_mode and self.db_ssl_mode != "disable":
            url += f"?ssl={self.db_ssl_mode}"
        return url

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def webhook_base(self) -> str:
        if self.vercel_url:
            return f"https://{self.vercel_url}"
        return "https://<your-domain>.vercel.app"

    @property
    def webhook_path(self) -> str:
        return "/webhook"

    @property
    def webhook_url(self) -> str:
        return f"{self.webhook_base}{self.webhook_path}"


config = Config()
