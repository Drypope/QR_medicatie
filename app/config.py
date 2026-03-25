from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_mode: str = "local"
    host: str = "127.0.0.1"
    port: int = 8765
    local_data_dir: Path = Path.home() / ".medmatrix"
    shared_source_dir: Path = Path(__file__).resolve().parents[1]
    catalog_file: str = "catalog.xlsx"
    presets_file: str = "presets.json"
    database_url: str | None = None
    auto_open_browser: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_prefix="MEDMATRIX_")

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        db_path = self.local_data_dir / "medmatrix.db"
        return f"sqlite:///{db_path}"

    @property
    def catalog_path(self) -> Path:
        return self.shared_source_dir / self.catalog_file

    @property
    def presets_path(self) -> Path:
        return self.shared_source_dir / self.presets_file


settings = Settings()
