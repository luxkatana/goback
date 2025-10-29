import tomllib
from sqlmodel import create_engine
from urllib.parse import urlparse
from typing import Any


class ConfigurationHolder:

    def __repr__(self) -> str:
        return f"ConfigurationHolder = {self.objects}"

    def __init__(self, **kwargs) -> None:
        object.__setattr__(self, "objects", kwargs)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "objects":
            return object.__setattr__(self, name, value)
        self.objects[name] = value

    def __getattribute__(self, name: str) -> Any | None:
        if name == "objects":
            return object.__getattribute__(self, name)
        return self.objects.get(name, None)


def get_working_database_string(
    config: ConfigurationHolder, debug_info: bool = True
) -> str:
    main_uri = config.db_connection_string
    secondary_uri = config.sqlite_fallback_filepath
    use_sqlite_as_second_option = config.use_sqlite_as_fallback_otpion
    try:
        engine = create_engine(main_uri)
        with engine.connect():
            return main_uri
    except Exception as e:
        if use_sqlite_as_second_option is True:
            if debug_info is True:
                print(f"WARNING: main uri ({main_uri}) does not work ({e})")
                print("-> Using sqlite as fallback option")
            return f"sqlite:///{secondary_uri}"
        raise e


def extract_db_uri(config_holder: ConfigurationHolder) -> dict[str, str]:
    url = urlparse(config_holder.db_connection_string)
    host = url.hostname
    port = url.port
    username = url.username
    password = url.password
    database = url.path[1::]
    return dict(host=host, port=port, user=username, password=password, db=database)


def get_tomllib_config() -> ConfigurationHolder:
    config_holder = ConfigurationHolder()
    with open("./goback.toml", "rb") as file:
        configuration = tomllib.load(file)

    for sections in configuration.values():
        for inner_key in sections:
            inner_val = sections[inner_key]
            setattr(config_holder, inner_key, inner_val)
    return config_holder


if __name__ == "__main__":
    _, holder = get_tomllib_config()
    print(holder.objects)
