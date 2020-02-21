import time

from app.clearing_operations import fetch_orders_for_clearing, clear_order
from app.configs import TICKER, GREEN_COLOR
from init_order_operations import place_order_init
from storage import get_init_order


def test_smoke():
    order_uid = place_order_init(1, 1, 1, 1, 225, 249, GREEN_COLOR, TICKER, False)['order_uid']

    res = clear_order('invalid uid')
    assert res is False
    assert order_uid in fetch_orders_for_clearing(0)
    assert get_init_order(order_uid)

    res = clear_order(order_uid)
    assert res is True
    time.sleep(3)
    assert order_uid not in fetch_orders_for_clearing(0)
    assert not get_init_order(order_uid)




