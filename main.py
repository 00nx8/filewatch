import json
import os 
import time
from watchdog.observers import Observer # type: ignore
from handler import Handler, request_unique_id
import asyncio

async def main():
    print('loading client...')
    
    directories = []
    config = None
    with open('head_directories.json') as f:
        head_directories = json.load(f)
        directories = normalize_directories(head_directories['directories'])
        config = head_directories['device']
        if head_directories['device']['device_id'] == 0:
            print('No device id found.')
            _id = await request_unique_id()
            print(f'Registering device with id: {_id}')
            config['device_id'] = _id
            head_directories['device']['device_id'] = _id
            with open('head_directories.json', 'w') as w:
                json.dump(head_directories, w)

    print('Loaded directories')

    initialize_observer(directories, config['device_id'])
    
    
def initialize_observer(directories, _id):
    observer = Observer()

    for directory in directories:
        observer.schedule(Handler(_id), path=directory, recursive=True)
        print(f'added directory {directory} to observer')

    observer.start()
    print('Started observer')

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print('stopped observer')
    observer.join()

def normalize_directories(dirs):
    """Replace <HOME> with pwd

    Args:
        dirs (list): directories

    Returns:
        list: updated directories
    """
    directories = []

    for dir in dirs:
        if dir.startswith('<HOME>'):
            dir = dir.replace('<HOME>', os.path.expanduser('~'))

        if os.path.isdir(dir) or os.path.isfile(dir):
            directories.append(dir)
            continue

        take_action = ask_choice(f"{dir}\n" + 'Directory or file does not exist. Would you like to create it?')
        res = handle_missing_entry(take_action, dir)
        if not res:
            print('Skipped, Either you chose to not create or files are not supported.')
            continue
        
        directories.append(dir)
        
    return directories

def handle_missing_entry(action, _dir) -> bool:
    """Returns true if the directory was created, false if file encountered or directory was not created.

    Args:
        action (bool): to create create missing entry or not
        dir (string): current entry in question

    Returns:
        bool: file/directory was created
    """
    if action:
        crumbs = _dir.split('/')
        is_file = len(crumbs[-1].split('.')) > 1
        if is_file:
            return False
        
        os.mkdir(_dir)
        return True
    
    to_remove = ask_choice('Would you like to remove the directory from the configuration file?')

    if not to_remove:
        return False

    with open('head_directories.json', 'r') as r:
        config = json.load(r)

        home = os.path.expanduser('~')

        if home in _dir:
            altered = _dir.replace(home, '<HOME>').lstrip('/')
        if altered in config['directories']:
            config['directories'].remove(altered)
        elif _dir in config['directories']:
            config['directories'].remove(_dir)

        else:
            print('Directory could not be removed. Please update your config file manually.')
            return False

        with open('head_directories.json', 'w') as w:
            json.dump(config, w)

    return True

def ask_choice(question):
    response = input(f"{question} (Y/n)")

    return response.lower() == 'y'

if __name__ == "__main__":    
    asyncio.run(main())