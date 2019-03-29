import asyncio
from asyncio import sleep
from time import time

import websockets.client as wsc
import json
from src.utils.config_loader import creds_conf

PUSHBULLET_STREAM = f"wss://stream.pushbullet.com/websocket/{creds_conf['pushbullet_access_token']}"
IB_SMS_NUMBER = "+41417269500"


def wait_for_ib_auth_message(timeout_sec):
    result = asyncio.get_event_loop().run_until_complete(_receive_pb_msgs(timeout_sec))

    return result


async def _receive_pb_msgs(timeout_sec):
    start_time = time()
    current_time = start_time
    async with wsc.connect(PUSHBULLET_STREAM) as ws:
        while current_time - start_time <= timeout_sec:
            jdata = await ws.recv()
            msg = json.loads(jdata)
            if _is_ib_sms_msg(msg):
                return _extract_sms_body_from_msg(msg)
            current_time = time()

            await sleep(.1)
    return None


def _extract_sms_body_from_msg(msg):
    return msg["push"]["notifications"][0]["body"]


def _is_ib_sms_msg(msg):
    if msg["type"] == "push":
        if msg["push"]["type"] == "sms_changed":
            if msg["push"]["notifications"][0]["title"] == IB_SMS_NUMBER:
                return True
    return False
