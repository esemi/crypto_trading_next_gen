import time

from app.configs import TICKER, GREEN_COLOR
from app.bitmex_ws import connect
from app.init_order_operations import place_order_init
from tests import TEST_LOW_PRICE, TEST_HIGH_PRICE


def test_smoke():
    client_ws = connect()
    last_event = client_ws.get_event()
    assert last_event is None

    order_uid = place_order_init(1, 1, 1, 1, TEST_LOW_PRICE, TEST_HIGH_PRICE, GREEN_COLOR, TICKER, False)['order_uid']
    time.sleep(3)
    last_event = client_ws.get_event()
    assert 'uid' in last_event
    assert 'status' in last_event
    assert last_event['uid'] == order_uid

    assert client_ws.get_event() is None


