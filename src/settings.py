"""
Project settings and configuration management.

Settings can be overridden via environment variables or a .env file.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from persiantools.jdatetime import JalaliDate


def _get_env(key: str, default: Any = None, cast: type = str) -> Any:
    """Get environment variable with optional type casting."""
    value = os.getenv(key, default)
    if value is None:
        return default
    if cast == bool:
        return str(value).lower() in ("true", "1", "yes")
    return cast(value)


@dataclass
class DatabaseSettings:
    """Database configuration."""
    file: str = field(default_factory=lambda: _get_env("DB_FILE", "market_data.db"))
    table_name: str = field(default_factory=lambda: _get_env("DB_TABLE", "market_data"))


@dataclass
class DateSettings:
    """Date range configuration."""
    start_year: int = field(default_factory=lambda: _get_env("START_YEAR", 1395, int))
    start_month: int = field(default_factory=lambda: _get_env("START_MONTH", 1, int))
    start_day: int = field(default_factory=lambda: _get_env("START_DAY", 1, int))
    end_year: int = field(default_factory=lambda: _get_env("END_YEAR", 1410, int))
    end_month: int = field(default_factory=lambda: _get_env("END_MONTH", 1, int))
    end_day: int = field(default_factory=lambda: _get_env("END_DAY", 1, int))

    @property
    def start_date(self) -> JalaliDate:
        return JalaliDate(self.start_year, self.start_month, self.start_day)

    @property
    def end_date(self) -> JalaliDate:
        return JalaliDate(self.end_year, self.end_month, self.end_day)


@dataclass
class APISettings:
    """API configuration."""
    timeout: int = field(default_factory=lambda: _get_env("API_TIMEOUT", 30, int))
    max_retries: int = field(default_factory=lambda: _get_env("API_MAX_RETRIES", 3, int))
    nfusion_token: str | None = field(default_factory=lambda: _get_env("NFUSION_TOKEN"))


@dataclass
class ChartSettings:
    """Chart configuration."""
    default_height: int = field(default_factory=lambda: _get_env("CHART_HEIGHT", 800, int))
    template: str = field(default_factory=lambda: _get_env("CHART_TEMPLATE", "plotly_white"))


@dataclass
class Settings:
    """Main settings container."""
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    dates: DateSettings = field(default_factory=DateSettings)
    api: APISettings = field(default_factory=APISettings)
    charts: ChartSettings = field(default_factory=ChartSettings)

    # Paths
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    events_file: str = field(default_factory=lambda: _get_env("EVENTS_FILE", "events.csv"))

    @property
    def events_path(self) -> Path:
        return self.base_dir / self.events_file

    @property
    def db_path(self) -> Path:
        return self.base_dir / self.database.file

    @classmethod
    def load_dotenv(cls) -> "Settings":
        """Load settings from .env file if it exists."""
        env_file = Path(__file__).parent.parent / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip())
        return cls()


# Global settings instance
settings = Settings.load_dotenv()
