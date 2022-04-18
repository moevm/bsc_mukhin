import dataclasses
import os
from datetime import datetime

from repository import Repository


@dataclasses.dataclass
class MeetingConfig:
    zoom_id: int
    name: str
    interval_days: int
    start_time: datetime
    host: str
    login: str
    password: str
    is_active: bool = True


@dataclasses.dataclass
class ScheduledMeeting:
    ts: datetime
    status: str


@dataclasses.dataclass
class Log:
    message: dict
    ts: datetime
    type: str


def get_repo() -> Repository:
    return Repository.create(os.environ['DB_URL'], echo=True)
