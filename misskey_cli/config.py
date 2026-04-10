import os
from pathlib import Path


CONFIG_DIR = Path(os.environ.get("MISSKEY_CLI_CONFIG_DIR", Path.home() / ".config" / "misskey-cli"))
DB_PATH = CONFIG_DIR / "config.db"


def _get(key, default=None):
    from .db import get_session, Config
    with get_session() as s:
        row = s.get(Config, key)
        return row.value if row else default


def _set(key, value):
    from .db import get_session, Config
    with get_session() as s:
        row = s.get(Config, key)
        if row:
            row.value = value
        else:
            s.add(Config(key=key, value=value))
        s.commit()


def get_token():
    return _get("token")


def get_host():
    return _get("host")


def get_default_visibility():
    return _get("default_visibility", "public")


def set_default_visibility(visibility):
    _set("default_visibility", visibility)


def save_credentials(host, token):
    _set("host", host)
    _set("token", token)
