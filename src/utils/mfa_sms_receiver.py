from asyncio import sleep
from time import time

from websocket import create_connection
import json
from src.utils.config_loader import creds_conf

PUSHBULLET_STREAM = f"wss://stream.pushbullet.com/websocket/{creds_conf['pushbullet_access_token']}"
# IB_SMS_NUMBER = "+41417269500"
IB_SMS_NUMBER = "+972544891512"


def wait_for_ib_auth_code(timeout_sec):
    res = _receive_pb_msgs(timeout_sec)
    code = None
    if res is not None:
        code = res.split(": ")[0]
    return code


def wait_for_ib_auth_message(timeout_sec):
    return _receive_pb_msgs(timeout_sec)


def _receive_pb_msgs(timeout_sec):
    start_time = time()
    current_time = start_time
    text = None

    ws = create_connection(PUSHBULLET_STREAM, timeout=10)

    try:
        while current_time - start_time <= timeout_sec:
            data = ws.recv()
            msg = json.loads(data)
            if _is_ib_sms_msg(msg):
                text = _extract_sms_body_from_msg(msg)
                break

            sleep(.1)
            current_time = time()
    finally:
        ws.close()

    return text


def _extract_sms_body_from_msg(msg):
    return msg["push"]["notifications"][0]["body"]


def _is_ib_sms_msg(msg):
    if msg["type"] == "push":
        if msg["push"]["type"] == "sms_changed":
            if msg["push"]["notifications"][0]["title"] == IB_SMS_NUMBER:
                return True
    return False


if __name__ == "__main__":
    s = time()
    msg = wait_for_ib_auth_message(10)
    e = time()
    print(msg)
    print(e - s)
