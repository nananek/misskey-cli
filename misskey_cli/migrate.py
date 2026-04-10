from pathlib import Path

from alembic.config import Config
from alembic import command

from . import config as _config_paths


def get_alembic_config():
    migrations_dir = Path(__file__).parent / "migrations"
    cfg = Config()
    cfg.set_main_option("script_location", str(migrations_dir))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{_config_paths.DB_PATH}")
    return cfg


def run_upgrade():
    _config_paths.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    cfg = get_alembic_config()
    command.upgrade(cfg, "head")
