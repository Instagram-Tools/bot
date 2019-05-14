import json

from env import settings

settings_json = json.dumps(settings).replace(" ", "")
