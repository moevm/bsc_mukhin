from urllib.parse import urlencode

import requests
from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse

from helper import (client_id, get_repo, redirect_uri, request_access_token,
                    zoom_url)

app = FastAPI()


@app.on_event('startup')
async def startup():
    await get_repo(echo=True, future=True)


@app.get("/")
async def root():
    return {"message": "Hello World"}


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
