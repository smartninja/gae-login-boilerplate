import os


def is_local():
    if os.environ.get('SERVER_NAME', '').startswith('localhost'):
        return True
    elif 'development' in os.environ.get('SERVER_SOFTWARE', '').lower():
        return True
    else:
        return False
