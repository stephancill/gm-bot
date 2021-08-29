import os

class ImproperlyConfigured(Exception):
    pass

def get_env_value(env_variable, default=None):
    try:
      	return os.environ[env_variable]
    except KeyError:
        if default != None:
            return default
        error_msg = 'Set the {} environment variable'.format(env_variable)
        raise ImproperlyConfigured(error_msg)

BOT_TOKEN = get_env_value("BOT_TOKEN")
CHANNEL_ID = get_env_value("CHANNEL_ID")
DEBUG = get_env_value("DEBUG", "false").lower() == "true"
APP_URL = get_env_value("APP_URL")
PORT = get_env_value("PORT")