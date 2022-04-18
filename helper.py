import base64
import dataclasses
import os
from datetime import datetime

import requests
from fastapi.security import HTTPBasic

from repository import Repository

security = HTTPBasic()


def request_access_token(code: str) -> dict:
    endpoint = '/oauth/token'
    authorization = f"{os.environ['CLIENT_ID']}:{os.environ['CLIENT_SECRET']}"
    secret_authorization = base64.b64encode(authorization.encode(encoding='utf-8')).decode('utf-8')
    headers = {
        'Authorization': f'Basic {secret_authorization}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    query_parameters = {
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': os.environ['REDIRECT_URI']+'/auth',
    }
    return requests.post(url=zoom_url+endpoint, headers=headers, params=query_parameters, timeout=5).json()


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
