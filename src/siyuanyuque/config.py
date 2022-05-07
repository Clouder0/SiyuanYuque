from __future__ import annotations

import atexit

from dynaconf import Dynaconf, Validator, loaders
from dynaconf.utils.boxing import DynaBox


settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["sqconfig.toml"],
    validators=[
        Validator("user_token", must_exist=True),
        Validator("api_host", default="https://www.yuque.com/"),
        Validator("last_sync_time", default="20220413224116"),
        Validator("siyuan_token", default=""),
        Validator("assets_replacement", default=None),
        Validator("custom_sync", default=[]),
    ],
)


@atexit.register
def write_config() -> None:
    data = settings.as_dict()
    loaders.write("sqconfig.toml", DynaBox(data).to_dict())
