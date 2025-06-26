import os

def find_applications():
    APP_DIRS = [
        '/Applications',
        os.path.expanduser('~/Applications'),
    ]
    apps = []
    for app_dir in APP_DIRS:
        if os.path.isdir(app_dir):
            for entry in os.listdir(app_dir):
                if entry.endswith('.app'):
                    app_name = entry[:-4]  # Remove .app
                    apps.append(app_name)
    return sorted(apps)
