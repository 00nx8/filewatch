from watchdog.events import FileSystemEventHandler, DirModifiedEvent, DirCreatedEvent, FileCreatedEvent, FileModifiedEvent, DirDeletedEvent, FileDeletedEvent
from typing import Optional, Dict, Any
from pathlib import Path
import requests
import os
import dotenv
from datetime import datetime
import websockets
import asyncio
import json
dotenv.load_dotenv()

API_PATH = os.environ['API_URL']

class Handler(FileSystemEventHandler):
    def __init__(self, _id):
        super().__init__()
        self._id = _id
        self.event = None
        self.target = None
        self.data_template = {
            'id': self._id,
            'path': '',
            'dest_path': '',
            'event_type': '',
            'is_directory': False
        }

    def on_modified(self, event):
        print(f"Modified: {event.src_path}")
        if not type(event) == FileModifiedEvent:
            return
        
        with open(event.src_path, 'rb') as f:
            data = self.data_template
            data['path'] = event.src_path
            data['event_type'] = event.event_type
            r = requests.post(
                url=API_PATH + f'/event/{event.event_type}',
                files={ 'files': f },
                data=self.data_template
            )

    def on_created(self, event):
        files: Optional[Dict[str, Any]] = {
            'files': None
        }

        if not event.is_directory:
            path = os.fsdecode(event.src_path)
            filename = Path(path).name

            with open(event.src_path, 'rb') as f:
                files['files'] = (filename, f.read())

        data = self.data_template

        data['path'] = event.src_path
        data['dest_path'] = event.dest_path or ''
        data['is_directory'] = event.is_directory
        data['event_type'] = event.event_type

        r = requests.post(
            url=API_PATH + f'/event/{event.event_type}',
            files=files,
            data=data
        )

    def on_deleted(self, event):
        r = requests.delete(
            url=API_PATH + f"/{event.event_type}",
            data={
                'path': event.src_path,
                'device_id': self._id
            }
        )

    def on_moved(self, event):
        data = self.data_template
        data['path'] = event.src_path
        data['dest_path'] = event.dest_path
        data['is_directory'] = event.is_directory

        r = requests.delete(
            url=API_PATH + f"/{event.event_type}",
            data=data
        )

async def submit_local_directories(directories, _id):
    return requests.post(
        url=f'{API_PATH}/submit_directories',
        data={
            'directories': directories,
            'device_id': _id
        }
    )

async def request_unique_id():
    r = requests.get(API_PATH + '/unique_id')
    data, status_code = json.loads(r.content.decode())

    if status_code != 200:
        return False

    return data['unique_id'] 
