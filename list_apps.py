#!/usr/bin/env python3
import os
import sys
import requests

# Directories to scan for applications on macOS
APP_DIRS = [
    '/Applications',
    os.path.expanduser('~/Applications'),
]

OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

def find_applications():
    apps = []
    for app_dir in APP_DIRS:
        if os.path.isdir(app_dir):
            for entry in os.listdir(app_dir):
                if entry.endswith('.app'):
                    apps.append(entry)
    return sorted(apps)

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
    print('Installed Applications:')
    for idx, app in enumerate(apps, 1):
        print(f'{idx}. {app}')
    try:
        choice = int(input('Select an app by number to ask ChatGPT about it (or 0 to exit): '))
    except ValueError:
        print('Invalid input.')
        return
    if choice == 0:
        return
    if not (1 <= choice <= len(apps)):
        print('Invalid selection.')
        return
    app_name = apps[choice - 1]
    question = input(f"What do you want to ask ChatGPT about '{app_name}'? ")
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print('Please set your OpenAI API key in the OPENAI_API_KEY environment variable.')
        return
    print('Asking ChatGPT...')
    answer = ask_chatgpt_about_app(app_name, question, api_key)
    print('\nChatGPT response:')
    print(answer)

if __name__ == '__main__':
    main()
