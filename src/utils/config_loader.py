import json

CREDS_FILE_PATH = "config/creds_live.json"


def read_config():
    with open(CREDS_FILE_PATH, "r") as creds_file:
        conf = json.load(creds_file)
    return conf


creds_conf = read_config()
