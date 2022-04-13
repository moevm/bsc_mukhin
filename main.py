from datetime import datetime
from urllib.parse import urlencode

import requests
from fastapi import Depends, FastAPI, status
from fastapi.responses import FileResponse, RedirectResponse
from starlette.middleware.cors import CORSMiddleware

from helper import (Meeting, client_id, get_account_by_name, get_repo,
                    redirect_uri, request_access_token, zoom_url)
from repository import Account, Repository

app = FastAPI()
security = HTTPBasic()
db = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return FileResponse('static/index.html')


@app.get('/api/v1/meetings')
async def get_meetings():
    return list(work_with_meetings.find({}, {'_id': False}))


@app.delete('/api/v1/meetings/{meeting_id}')
async def get_meeting_info(meeting_id: int):
    work_with_meetings.delete_one({'id': meeting_id})
    return {'success': True}


@app.post('/api/v1/meetings')
async def create_meeting(meeting_info: Meeting):
    meet = asdict(meeting_info)
    work_with_meetings.insert_one(meet.copy())
    return {'success': True} | meet


@app.get('/sign_in')
async def sign_in():
    params = {'response_type': 'code', 'client_id': client_id, 'redirect_uri': redirect_uri}
    endpoint = '/oauth/authorize'
    redirect_url = f'{zoom_url}{endpoint}?{urlencode(params)}/auth'
    return RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)


@app.get("/auth")
async def auth(code: str):
    response = request_access_token(code)
    if response.get('reason') == 'Invalid authorization code':
        return {'error': 'authorization code is expired'}
    token = response['access_token']
    get_meetings_url = 'https://api.zoom.us/v2/users/me/meetings'
    headers = {'Authorization': f'Bearer {token}'}
    meetings = requests.get(get_meetings_url, params={'page_size': 300}, headers=headers)
    return meetings.json()
