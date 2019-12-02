from app.bitmex_rest import cancel_all
from app.storage import gen_uid
from app.trader import place_orders_profit
from app.configs import TICKER, GREEN_COLOR, RED_COLOR


def test_success_green():
    """
    By long init order

    """

    r = place_orders_profit(124, 93, 20, GREEN_COLOR, TICKER, 'green_stop_order', 'green_take_order', True)
    assert isinstance(r, dict)

    assert 'stop' in r
    assert 'uid' in r['stop']
    assert 'qty' in r['stop']
    assert 'price' in r['stop']
    assert 'response' in r['stop']
    assert r['stop']['uid'] == 'green_stop_order'
    assert r['stop']['qty'] == -20.
    assert r['stop']['price'] == 93.

    assert 'take' in r
    assert 'uid' in r['take']
    assert 'qty' in r['take']
    assert 'price' in r['take']
    assert 'response' in r['take']
    assert r['take']['uid'] == 'green_take_order'
    assert r['take']['qty'] == -20.
    assert r['take']['price'] == 124.


def test_success_green_real():
    """
    By long init order

    """
    cancel_all(comment='unittest test_success_green_real')

    stop_uid = ('green_stop_order' + gen_uid())[:36]
    take_uid = ('green_take_order' + gen_uid())[:36]
    r = place_orders_profit(124, 93, 20, GREEN_COLOR, TICKER, stop_uid, take_uid, False)

    assert r['stop']['uid'] == stop_uid
    assert r['take']['uid'] == take_uid
    assert r['stop']['response'] != 'dry run'
    assert r['take']['response'] != 'dry run'


def test_success_red():
    """
    By short init order

    """
    r = place_orders_profit(90, 123, 20, RED_COLOR, TICKER, 'red_stop_order', 'red_take_order', True)
    assert isinstance(r, dict)

    assert 'stop' in r
    assert 'uid' in r['stop']
    assert 'qty' in r['stop']
    assert 'price' in r['stop']
    assert 'response' in r['stop']
    assert r['stop']['uid'] == 'red_stop_order'
    assert r['stop']['qty'] == 20.
    assert r['stop']['price'] == 123.

    assert 'take' in r
    assert 'uid' in r['take']
    assert 'qty' in r['take']
    assert 'price' in r['take']
    assert 'response' in r['take']
    assert r['take']['uid'] == 'red_take_order'
    assert r['take']['qty'] == 20.
    assert r['take']['price'] == 90.


def test_success_red_real():
    """
    By short init order

    """
    cancel_all(comment='unittest test_success_red_real')

    stop_uid = ('red_stop_order' + gen_uid())[:36]
    take_uid = ('red_take_order' + gen_uid())[:36]
    r = place_orders_profit(90, 123, 20, RED_COLOR, TICKER, stop_uid, take_uid, False)

    assert r['stop']['uid'] == stop_uid
    assert r['take']['uid'] == take_uid
    assert r['stop']['response'] != 'dry run'
    assert r['take']['response'] != 'dry run'