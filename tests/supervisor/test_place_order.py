from configs import RED_COLOR, GREEN_COLOR, TICKER
from crypto_bot.supervisor import place_order

offset = 1.


def test_small_bucket():
    r = place_order(5, 10, 15, GREEN_COLOR, TICKER, True)
    assert r is None


def test_success_green():
    """
    Long order

    """

    r = place_order(offset, 10, 15, GREEN_COLOR, TICKER, True)
    assert isinstance(r, dict)
    assert 'qty' in r
    assert 'init_price' in r
    assert 'stop_price' in r
    assert 'take_price' in r
    assert 'order_uid' in r
    assert 'response' in r
    assert r['order_uid']
    assert r['response']
    assert r['init_price'] == 16
    assert r['stop_price'] == 9
    assert r['take_price'] == 20
    assert r['qty'] > 0.


def test_success_red():
    """
    Short order

    """

    r = place_order(offset, 10, 15, RED_COLOR, TICKER, True)
    assert isinstance(r, dict)
    assert 'qty' in r
    assert 'init_price' in r
    assert 'stop_price' in r
    assert 'take_price' in r
    assert 'order_uid' in r
    assert 'response' in r
    assert r['order_uid']
    assert r['response']
    assert r['init_price'] == 9
    assert r['stop_price'] == 16
    assert r['take_price'] == 5
    assert r['qty'] < 0.


def test_real_place_order():
    r = place_order(offset, 10, 15, GREEN_COLOR, TICKER, False)
    assert isinstance(r, dict)
    assert 'qty' in r
    assert 'init_price' in r
    assert 'stop_price' in r
    assert 'take_price' in r
    assert 'order_uid' in r
    assert 'response' in r
    assert 'orderID' in r['response']
    assert r['response']['orderID']
