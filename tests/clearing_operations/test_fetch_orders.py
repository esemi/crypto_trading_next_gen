import time

from app.clearing_operations import fetch_orders_for_clearing
from app.configs import TICKER, GREEN_COLOR
from bitmex_rest import cancel_all
from init_order_operations import place_order_init


def test_smoke():
    cancel_all('unittest clearing operations 1')
    time.sleep(3)

    order_uid1 = place_order_init(1, 1, 1, 1, 225, 249, GREEN_COLOR, TICKER, False)['order_uid']
    order_uid2 = place_order_init(1, 1, 1, 1, 228, 290, GREEN_COLOR, TICKER, False)['order_uid']
    orders = fetch_orders_for_clearing()
    assert orders == []

    orders = fetch_orders_for_clearing(0)
    assert len(orders) == 2
    assert order_uid1 in orders
    assert order_uid2 in orders

    cancel_all('unittest clearing operations 1')
    time.sleep(3)
    orders = fetch_orders_for_clearing(0)
    assert orders == []



