import time

from configs import TICKER, GREEN_COLOR
from crypto_bot.bitmex_api import client_ws
from crypto_bot.supervisor import place_order


def test_smoke():
    last_event = client_ws.get_event()
    assert last_event is None

    order_uid = place_order(1, 1, 4300, 4700, GREEN_COLOR, TICKER, False)['order_uid']
    time.sleep(10)
    last_event = client_ws.get_event()
    assert 'uid' in last_event
    assert 'status' in last_event
    assert last_event['uid'] == order_uid

    assert client_ws.get_event() is None

