from datetime import datetime
from secrets import randbits
from enum import Enum
import pickle
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Session, create_engine
from pwdlib import PasswordHash
from config_manager import (
    ConfigurationHolder,
    get_tomllib_config,
    get_working_database_string,
)

SECRET_KEY = "".join([chr(randbits(8)) for _ in range(50)])
hasher = PasswordHash.recommended()

conf_holder: ConfigurationHolder = get_tomllib_config()

db_string = get_working_database_string(conf_holder)

db_engine = create_engine(db_string)


class StatusTypesEnum(Enum):
    SUCCESS = 0
    INFO = 1
    ERROR = 2
    FAILED = 3
    def __repr__(self) -> str:
        return self.__str__()
    def __str__(self) -> str:
        match self.value:
            case 0:
                return "Status-Success"
            case 1:
                return "Status-Info"
            case 2:
                return "Status-Error"
            case 3:
                return "Status-Failed"

def get_db_session():
    try:
        with Session(db_engine) as session:
            yield session

    finally:
        session.close()


def setup_tables():
    SQLModel.metadata.drop_all(db_engine)
    SQLModel.metadata.create_all(db_engine)


class User(SQLModel, table=True):
    __tablename__ = "goback_users"
    user_id: int | None = Field(primary_key=True)
    username: str = Field(max_length=50, nullable=False, min_length=10)
    email: str = Field(max_length=255, nullable=False)
    password: str = Field(max_length=255, nullable=False, min_length=8)

    def __repr__(self) -> str:
        return f"User({self.user_id},{self.username},{self.email},{self.password})"


class AssetMetadata(SQLModel, table=True):
    __tablename__ = "goback_assets_metadata"
    asset_id: int | None = Field(primary_key=True)
    original_asset_html: str = Field(nullable=False, max_length=64)
    file_id: str = Field(nullable=False, max_length=36)
    mimetype: str = Field(default="any")




class Status(BaseModel):
    message: str
    status_type: StatusTypesEnum


class JobTask(SQLModel, table=True):
    __tablename__ = "goback_job_tracker"
    job_id: int | None = Field(primary_key=True)
    user_id: int = Field(nullable=False, foreign_key="goback_users.user_id")
    created_at: datetime
    status_messages: bytes = Field()  # list[Status]

    def add_status_message(
        self, message: str, statustype: StatusTypesEnum = StatusTypesEnum.INFO
    ):
        deserialized: list[Status] = pickle.loads(self.status_messages)
        deserialized.append(Status(message=message, status_type=statustype))
        self.status_messages = pickle.dumps(deserialized)

    def as_dict(self) -> dict[str, str]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


SQLModel.metadata.create_all(db_engine)
if __name__ == "__main__":
    setup_tables()
