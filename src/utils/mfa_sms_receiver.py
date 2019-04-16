from threading import Thread
from time import time, sleep
from src.logger import logger
from websocket import create_connection
import json
from src.utils.config_loader import creds_conf

PUSHBULLET_STREAM = f"wss://stream.pushbullet.com/websocket/{creds_conf['pushbullet_access_token']}"
IB_SMS_NUMBER = "+41417269500"
# IB_SMS_NUMBER = "+972544891512"


class MFASMSReceiver:
    def __init__(self, timeout):
        self._timeout = timeout
        self._receiver_thread = Thread(target=self._receive_pb_msgs)
        self._received_auth_code = None
        self._timeout_reached = False

    def start_listening_for_auth_code(self):
        self._receiver_thread.start()

        sleep(3)

    @property
    def auth_code(self):
        if self._received_auth_code is None and not self._timeout_reached:
            self._receiver_thread.join()

        return self._received_auth_code

    def _receive_pb_msgs(self):
        start_time = time()
        current_time = start_time
        text = None

        ws = create_connection(PUSHBULLET_STREAM, timeout=self._timeout)

        try:
            while current_time - start_time <= self._timeout:
                data = ws.recv()
                msg = json.loads(data)
                if self._is_ib_sms_msg(msg):
                    text = self._extract_auth_code_from_msg(msg)
                    self._received_auth_code = text
                    break

                sleep(.1)
                current_time = time()
        finally:
            ws.close()
        return text

    @staticmethod
    def _extract_auth_code_from_msg(msg):
        body = msg["push"]["notifications"][0]["body"]
        code = body.split(": ")[1]

        return code

    @staticmethod
    def _is_ib_sms_msg(msg):
        if msg["type"] == "push":
            if msg["push"]["type"] == "sms_changed":
                if msg["push"]["notifications"][0]["title"] == IB_SMS_NUMBER:
                    return True
        return False


if __name__ == "__main__":
    r = MFASMSReceiver(30)
