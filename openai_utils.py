import requests
import time

OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'

def get_app_description(app_name, api_key, cache, save_cache_func):
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
    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            desc = response.json()['choices'][0]['message']['content'].strip()
        else:
            print(f"Error fetching description for {app_name}: {response.status_code} - {response.text}")
            desc = 'Unknown'
    except Exception as e:
        print(f"Exception fetching description for {app_name}: {e}")
        desc = 'Unknown'
    cache[app_name] = desc
    save_cache_func(cache)
    return desc

def find_best_app_by_description(apps, api_key, description, cache, save_cache_func):
    app_descriptions = {}
    for app in apps:
        desc = get_app_description(app, api_key, cache, save_cache_func)
        app_descriptions[app] = desc
        if app not in cache:
            time.sleep(0.7)  # To avoid hitting rate limits only for new queries
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
    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            print(f"Error matching app by description: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception matching app by description: {e}")
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
    try:
        response = requests.post(OPENAI_API_URL, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            print(f"Error asking about app: {response.status_code} - {response.text}")
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        print(f"Exception asking about app: {e}")
        return f"Exception: {e}"

def check_openai_subscription(api_key):
    url = 'https://api.openai.com/v1/dashboard/billing/subscription'
    headers = {
        'Authorization': f'Bearer {api_key}',
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            plan = data.get('plan', {}).get('title', 'Unknown')
            hard_limit_usd = data.get('hard_limit_usd', 'Unknown')
            print(f"OpenAI Subscription Plan: {plan}")
            print(f"Hard Limit (USD): {hard_limit_usd}")
        else:
            print(f"Error checking OpenAI subscription: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Exception checking OpenAI subscription: {e}")
