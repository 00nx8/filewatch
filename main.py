import json
import os 
import time
from watchdog.observers import Observer # type: ignore
from handler import Handler, request_unique_id, submit_local_directories
import pprint
import asyncio

async def main():
    print('loading client...')
    
    directories = []
    config = None
    
    with open('head_directories.json') as f:
        head_directories = json.load(f)
        directories = normalize_directories(head_directories['directories'])
        config = head_directories['device']

        if not config['device_id'] or config['device_id'] == 0:
            print('No device id found.')
            _id = await request_unique_id()
        
            print(f'Registering device with id: {_id}')
            config['device_id'] = _id
            head_directories['device']['device_id'] = _id
            with open('head_directories.json', 'w') as w:
                json.dump(head_directories, w)
        
        print('Sending local directories to remote.')        
        res = await submit_local_directories(directories, config['device_id'])
        data = json.loads(res.content.decode())
        if (data.get('made_directories')):
            print('Directories found that dont exist on remote.')
            directories_of_made = get_untracked_files(data.get('made_directories'))
            # TODO send to backend

        
        print(data)
            
    print('Loaded directories')

    initialize_observer(directories, config['device_id'])

tree = {
    '/projects': {

    }
}

def get_untracked_files(dirs):
    tree = []
    for _dir in dirs:
        tree.append(discover_directory(_dir))     

    pprint.pp(tree)

def discover_directory(_dir):
    tree = {
        'directory': _dir
    }
    tree['sub_directories'] = []
    tree['files'] = []

    for entry in os.listdir(_dir):
        path = f'{_dir}/{entry}'
        if os.path.isdir(path):
            sub_dirs = discover_directory(path)
            tree['sub_directories'].append(sub_dirs)
            continue

        with open(path, 'rb') as f:
            tree['files'].append((
                entry, f.read()
            ))

    return tree


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
    """Determine what to do if monitored entry is missing on local.

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
    # asyncio.run(main())
    get_untracked_files([
        '/home/tuzma/Documents/projects'
    ])