from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware

from helper import (get_repo, MeetingConfig, ScheduledMeeting, Log)
from repository import Repository

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
def on_startup():
    get_repo()


@app.get('/')
async def root():
    return FileResponse('static/index.html')


@app.get('/api/v1/meeting_config')
async def get_meetings(repo: Repository = Depends(get_repo)):
    return repo.get_meetings()


@app.delete('/api/v1/meeting_config/{meeting_id}')
async def change_meeting(meeting_id: int, repo: Repository = Depends(get_repo)):
    repo.delete_meeting(meeting_id)
    return {'success': True}


@app.post('/api/v1/meeting_config')
async def create_meeting_config(meeting_config: MeetingConfig, repo: Repository = Depends(get_repo)):
    meeting_config.__dict__.pop('__initialised__')
    repo.add_meeting_config(meeting_config.__dict__)
    return {'success': True} | meeting_config.__dict__


@app.post('/api/v1/scheduled_meeting/{meeting_config_id}')
async def create_scheduled_meeting(zoom_id: int, config: ScheduledMeeting, repo: Repository = Depends(get_repo)):
    config.__dict__.pop('__initialised__')
    repo.add_scheduled_meeting(zoom_id, config.__dict__)
    return {'success': True} | config.__dict__


@app.post('/api/v1/log/{scheduled_meeting_id}')
async def create_log(scheduled_meeting_id: int, log: Log, repo: Repository = Depends(get_repo)):
    log.__dict__.pop('__initialised__')
    repo.add_log(scheduled_meeting_id, log.__dict__)
    return {'success': True} | log.__dict__
