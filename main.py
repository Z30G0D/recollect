import os
from apps import find_applications
from cache import load_cache, save_cache
from openai_utils import find_best_app_by_description, ask_chatgpt_about_app

def main():
    apps = find_applications()
    if not apps:
        print('No applications found.')
        return
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print('Please set your OpenAI API key in the OPENAI_API_KEY environment variable.')
        return
    print('Note: To check your OpenAI subscription plan or usage, visit:')
    print('https://platform.openai.com/account/usage')
    print('https://platform.openai.com/account/billing/overview')
    cache = load_cache()
    print('Installed Applications:')
    for idx, app in enumerate(apps, 1):
        print(f'{idx}. {app}')
    print('\n--- App Finder by Description ---')
    description = input('Describe the app you are looking for (e.g., "photo editor"): ')
    print('Finding the best match (this may take a minute the first time)...')
    best_match = find_best_app_by_description(apps, api_key, description, cache, save_cache)
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
