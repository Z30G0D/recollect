#!/usr/bin/env python3
import os
import sys
import requests
import time
import json

# This file is now split into modules:
# - main.py: main entry point
# - apps.py: app finding logic
# - cache.py: cache logic
# - openai_utils.py: OpenAI API logic
# You can run the app with: python3 main.py

# Directories to scan for applications on macOS
APP_DIRS = [
    '/Applications',
    os.path.expanduser('~/Applications'),
]
CACHE_FILE = 'app_descriptions_cache.json'
OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

def find_applications():
    apps = []
    for app_dir in APP_DIRS:
        if os.path.isdir(app_dir):
            for entry in os.listdir(app_dir):
                if entry.endswith('.app'):
                    # Clean up app name
                    app_name = entry[:-4]  # Remove .app
                    apps.append(app_name)
    return sorted(apps)

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def get_app_description(app_name, api_key, cache):
    if app_name in cache:
        return cache[app_name]
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    prompt = f"In one short sentence, what does the macOS application '{app_name}' do? If you don't know, say 'Unknown'."
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'user', 'content': prompt}
        ]
    }
    response = requests.post(OPENAI_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        desc = response.json()['choices'][0]['message']['content'].strip()
    else:
        desc = 'Unknown'
    cache[app_name] = desc
    save_cache(cache)
    return desc

def find_best_app_by_description(apps, api_key, description, cache):
    # Get descriptions for each app (with basic caching to avoid repeated API calls)
    app_descriptions = {}
    for app in apps:
        desc = get_app_description(app, api_key, cache)
        app_descriptions[app] = desc
        if app not in cache:
            time.sleep(0.7)  # To avoid hitting rate limits only for new queries
    # Build prompt for ChatGPT
    app_list = '\n'.join([f"{app}: {desc}" for app, desc in app_descriptions.items()])
    prompt = (
        f"Given the following list of macOS applications and their descriptions:\n{app_list}\n"
        f"Which application best matches this description: '{description}'? "
        "Return only the app name from the list. If none match, say 'None'."
    )
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'user', 'content': prompt}
        ]
    }
    response = requests.post(OPENAI_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content'].strip()
    else:
        return None

def ask_chatgpt_about_app(app_name, question, api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    prompt = f"Tell me about the macOS application '{app_name}'. {question}"
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'user', 'content': prompt}
        ]
    }
    response = requests.post(OPENAI_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Error: {response.status_code} - {response.text}"

def main():
    apps = find_applications()
    if not apps:
        print('No applications found.')
        return
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print('Please set your OpenAI API key in the OPENAI_API_KEY environment variable.')
        return
    cache = load_cache()
    print('Installed Applications:')
    for idx, app in enumerate(apps, 1):
        print(f'{idx}. {app}')
    print('\n--- App Finder by Description ---')
    description = input('Describe the app you are looking for (e.g., "photo editor"): ')
    print('Finding the best match (this may take a minute the first time)...')
    best_match = find_best_app_by_description(apps, api_key, description, cache)
    if best_match and best_match in apps:
        print(f"\nBest match: {best_match}")
        ask = input(f"Do you want to ask ChatGPT more about '{best_match}'? (y/n): ")
        if ask.lower() == 'y':
            question = input(f"What do you want to ask about '{best_match}'? ")
            print('Asking ChatGPT...')
            answer = ask_chatgpt_about_app(best_match, question, api_key)
            print('\nChatGPT response:')
            print(answer)
    else:
        print('Could not find a matching app.')

if __name__ == '__main__':
    main()
