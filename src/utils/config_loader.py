import json

from src.utils.ib_gateway_launcher import CREDS_FILE_PATH

with open(CREDS_FILE_PATH, "r") as creds_file:
    creds_conf = json.load(creds_file)
