import base64
import os

import requests

from repository import Repository

zoom_url = 'https://zoom.us'
client_id = os.environ['CLIENT_ID']
redirect_uri = os.environ['REDIRECT_URI']


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


async def get_repo(db_url=os.environ['DB_URL'], **kwargs):
    return await Repository.create(db_url, **kwargs)
