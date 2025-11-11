from io import BytesIO
import tomllib
from rich import print
from sqlmodel import create_engine
import httpx
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
    use_sqlite_as_second_option = config.use_sqlite_as_fallback_option
    try:
        engine = create_engine(main_uri)
        with engine.connect():
            return main_uri
    except Exception as e:
        if use_sqlite_as_second_option is True:
            if debug_info is True:
                print(
                    f"[yellow bold]WARNING[/yellow bold]: main uri ({main_uri}) does not work ({e})"
                )
                print("[white]-> Using sqlite as fallback option[/white]")
            return f"sqlite:///{secondary_uri}"
        raise e


def validate_appwrite_credentials(holder: ConfigurationHolder):
    endpoint_url = holder.endpoint_url
    api_key = holder.api_key
    project_id = holder.project_id
    headers = {
        "X-Appwrite-Project": project_id,
        "X-Appwrite-Key": api_key,
    }
    storage_bucket_id = holder.storage_bucket_id
    if None in (endpoint_url, api_key, project_id, storage_bucket_id):
        print(
            "[red bold]ERROR[/red bold]: Missing some valid appwrite variables (possibly some info is missing, check the default template in the github repo)"
        )
        exit(1)

    if not endpoint_url.startswith(
        "http"
    ):  # Not a valid url, dumb checking but it works
        print(
            "[red bold]ERROR[/red bold]: Appwrite URL endpoint is invalid, perhaps it's not starting with http or https:// "
        )
        exit(1)

    with BytesIO() as io:
        io.write(b"Validation success")
        response = httpx.post(
            f"{endpoint_url}/storage/buckets/{storage_bucket_id}/files",
            headers=headers,
            data={"fileId": "validationifcredentialsareok"},
            files={"file": ("validationfile.txt", io, "text/plain")},
        )
        # 201 is what we should get
        # 409 already exists
        if response.status_code == 401:
            if response.json()["type"] == "user_unauthorized":
                print(
                    "[red bold]ERROR[/red bold]: API key is invalid (api_key field in goback.toml)"
                )
            elif response.json()["type"] == "general_unauthorized_scope":
                print(
                    "[red bold]ERROR[/red bold]: missing scopes, make sure that the api key has the files.read and files.write scopes enabled"
                )

            exit(1)
        if response.status_code == 404:
            if response.json()["type"] == "project_not_found":
                print("[red bold]ERROR[/red bold]: Project ID is invalid")
            elif response.json()["type"] == "storage_bucket_not_found":
                print("[red bold]ERROR[/red bold]: Storage bucket is invalid")

            exit(1)

        response = httpx.get(
            f"{endpoint_url}/storage/buckets/{storage_bucket_id}/files/validationifcredentialsareok/preview",
            headers=headers,
        )
        if (
            response.status_code == 401
            and response.json()["type"] == "general_unauthorized_scope"
        ):
            print(
                "[red bold]ERROR[/red bold]: missing scopes, make sure that the api key has the files.read and files.write scopes enabled"
            )
            exit(1)

        httpx.delete(
            f"{endpoint_url}/storage/buckets/{storage_bucket_id}/files/validationifcredentialsareok",
            headers=headers,
        ).raise_for_status()
        print(
            ":tada: Appwrite credentials validations passed :white_check_mark: :tada:"
        )


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
    holder = get_tomllib_config()

    (validate_appwrite_credentials(holder))
