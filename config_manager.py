import tomllib
from urllib.parse import urlparse
from typing import NamedTuple


class ConfigurationHolder(NamedTuple):
    sqlalchemy_connection_uri: str
    use_sqlite_memory_as_fallback_option: bool
    api_key: str
    endpoint_url: str
    project_id: str
    storage_bucket_id: str
    webserver_host: str
    webserver_port: int
    debug_mode: bool
    media_url: str


def extract_db_uri(config_holder: ConfigurationHolder) -> dict[str, str]:
    url = urlparse(config_holder.sqlalchemy_connection_uri)
    host = url.hostname
    port = url.port
    username = url.username
    password = url.password
    database = url.path[1::]
    return dict(
        host=host, port=port, username=username, password=password, database=database
    )


def get_tomllib_config() -> tuple[bool, ConfigurationHolder | str | Exception]:
    valid_form: dict[str] = {}
    with open("./goback.toml", "rb") as file:
        configuration = tomllib.load(file)

    for sections in configuration.values():
        for inner_key in sections:
            inner_val = sections[inner_key]
            valid_form[inner_key] = inner_val
    try:
        return (True, ConfigurationHolder(**valid_form))
    except TypeError:
        return (
            False,
            "Invalid configuration, please check your configuration file (goback.toml)",
        )

    except Exception as e:
        return (False, e)


if __name__ == "__main__":
    _, holder = get_tomllib_config()
    print(extract_db_uri(holder))
