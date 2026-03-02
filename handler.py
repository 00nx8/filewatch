from watchdog.events import FileSystemEventHandler # type: ignore
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
    def __init__(self):
        super().__init__()
        self.event = None
        self.target = None

    def on_modified(self, event):
        print(f"Modified: {event.src_path}")
        self.event = 'modified'
        self.send_update()
    
    def on_created(self, event):
        print(f"Created: {event.src_path}")
        self.event = 'created'
        self.send_update()

    def on_deleted(self, event):
        print(f"Deleted: {event.src_path}")
        self.event = 'deleted'
        self.send_update()

    def on_moved(self, event):
        print(f"Moved: {event.src_path} to {event.dest_path}")
        self.event = 'moved'
        self.send_update()

    def send_update(self):
        r = requests.post(API_PATH + f'/event/{self.event}')
        print(r)


async def connect():
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        print('Connected')
        await ws.send(json.dumps({
            'last_seen': datetime.now().isoformat(),
            'device_id': '',
        }))
        async for message in ws:
            print(message)

async def request_unique_id():
    r = requests.get(API_PATH + '/unique_id')
    data, status_code = json.loads(r.content.decode())

    if status_code != 200:
        return False

    return data['unique_id'] 


# PROTOCOL
# New device:
# request unique id,
# save
# go through added directories, note down last modified for files.
# send to server
# 