import hashlib
import hmac
import json
import logging
import threading
import time
import urllib
from queue import Queue, Empty
from time import sleep
from typing import Optional

import websocket

from configs import API_KEY, API_SECRET


class CustomBitmexWS:
    """
    Copy-paste of from bitmex_websocket import BitMEXWebsocket
    Original class too big and dirty for us

    """

    def __init__(self, endpoint, api_key=None, api_secret=None):
        """Connect to the websocket and initialize data stores."""

        self._events = Queue()
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing WebSocket.")
        self.endpoint = self.__prepare_wss_endpoint(endpoint)
        self.exited = False

        self.api_key = api_key
        self.api_secret = api_secret

        self.logger.info(f'Connecting to {self.endpoint}')
        self.__connect()
        self.logger.info('Connected to WS.')

    def exit(self):
        """Call this to exit - will close websocket."""
        self.exited = True
        self.ws.close()

    def __connect(self):
        """Connect to the websocket in a thread."""

        self.logger.debug("Starting thread")
        self.ws = websocket.WebSocketApp(self.endpoint,
                                         on_message=self.__on_message,
                                         on_close=self.__on_close,
                                         on_open=self.__on_open,
                                         on_error=self.__on_error,
                                         header=self.__get_auth())

        self.wst = threading.Thread(target=lambda: self.ws.run_forever())
        self.wst.daemon = True
        self.wst.start()
        self.logger.debug("Started thread")

        # Wait for connect before continuing
        conn_timeout = 5
        while not self.ws.sock or not self.ws.sock.connected and conn_timeout:
            sleep(1)
            conn_timeout -= 1
        if not conn_timeout:
            self.logger.error("Couldn't connect to WS! Exiting.")
            self.exit()
            raise websocket.WebSocketTimeoutException('Couldn\'t connect to WS! Exiting.')

    def __get_auth(self):
        """Return auth headers. Will use API Keys if present in settings."""

        self.logger.info("Authenticating with API Key.")

        expires = int(round(time.time() + 3600))
        parsed_url = urllib.parse.urlparse('/realtime')
        path = parsed_url.path
        if parsed_url.query:
            path = path + '?' + parsed_url.query
        message = ('GET' + path + str(expires)).encode('utf-8')
        signature = hmac.new(self.api_secret.encode('utf-8'), message, digestmod=hashlib.sha256).hexdigest()

        return [
            f'api-expires: {str(expires)}',
            f'api-signature: {signature}',
            f'api-key: {self.api_key}'
        ]

    @staticmethod
    def __prepare_wss_endpoint(endpoint: str):
        url_parts: list = list(urllib.parse.urlparse(endpoint))
        url_parts[0] = url_parts[0].replace('http', 'ws')
        url_parts[2] = "/realtime?subscribe=order"
        # url_parts[2] .= ",trade:XBTUSD"
        return urllib.parse.urlunparse(url_parts)

    def __on_message(self, message):
        """Handler for parsing WS messages."""

        message = json.loads(message)

        table = message.get("table")
        action = message.get("action")
        source = message.get('data')
        self.logger.debug(f'receive message: {json.dumps(message)}')

        if table == 'order' and action in ('insert', 'update') and source:
            self.logger.debug(f'{table}-{action}: new event {source}')
            for source_event in source:
                self.logger.info(f'process event {source_event}')
                order_uid = source_event.get('clOrdID', '')
                status = source_event.get('ordStatus', '')
                if status != 'Filled':
                    self.logger.info(f'skip event {order_uid} {status}')
                    continue
                event = {'uid': order_uid, 'status': status}
                self._events.put(event, block=False)
                self.logger.info(f'add new event={event}')

        else:
            self.logger.debug('message ignored')

    def __on_error(self, error):
        """Called on fatal websocket errors. We exit on these."""

        if not self.exited:
            self.logger.error("Error : %s" % error)
            self.exit()
            raise websocket.WebSocketException(error)

    def __on_open(self):
        """Called when the WS opens."""

        self.logger.debug("Websocket Opened.")

    def __on_close(self):
        """Called on websocket close."""
        self.exit()
        self.logger.info('Websocket Closed')

    def get_event(self) -> Optional[dict]:
        try:
            return self._events.get(block=False)
        except Empty:
            return None

    def iter_events(self) -> dict:
        yield self._events.get(block=True)


def connect() -> CustomBitmexWS:
    from bitmex_rest import client_rest
    logging.info(f'connect to {client_rest.swagger_spec.api_url} by {API_KEY}')
    return CustomBitmexWS(endpoint=client_rest.swagger_spec.api_url, api_key=API_KEY, api_secret=API_SECRET)
