import tomllib
from urllib.parse import urlparse
from typing import Any

# TODO: get rid of the aiomysql module, and use sqlalchemy


class ConfigurationHolder:

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


def extract_db_uri(config_holder: ConfigurationHolder) -> dict[str, str]:
    url = urlparse(config_holder.sqlalchemy_connection_uri)
    host = url.hostname
    port = url.port
    username = url.username
    password = url.password
    database = url.path[1::]
    return dict(host=host, port=port, user=username, password=password, db=database)


def get_tomllib_config() -> tuple[bool, ConfigurationHolder | str | Exception]:
    config_holder = ConfigurationHolder()
    with open("./goback.toml", "rb") as file:
        configuration = tomllib.load(file)

    for sections in configuration.values():
        for inner_key in sections:
            inner_val = sections[inner_key]
            setattr(config_holder, inner_key, inner_val)
    try:
        return (True, config_holder)
    except TypeError:
        return (
            False,
            "Invalid configuration, please check your configuration file (goback.toml)",
        )

    except Exception as e:
        return (False, e)


if __name__ == "__main__":
    _, holder = get_tomllib_config()
    print(holder.objects)
