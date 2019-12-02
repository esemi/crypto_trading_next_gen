from app.configs import RED_COLOR, GREEN_COLOR, TICKER
from app.storage import get_init_order
from app.supervisor import place_order_init

offset = 2.


def test_small_bucket():
    r = place_order_init(5, 5, 10, 15, GREEN_COLOR, TICKER, True)
    assert r is None


def test_success_green():
    """
    Long order

    """

    r = place_order_init(offset, offset, 10, 15, GREEN_COLOR, TICKER, True)
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


def test_success_red():
    """
    Short order

    """

    r = place_order_init(offset, offset, 10, 15, RED_COLOR, TICKER, True)
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


def test_real_place_order():
    r = place_order_init(offset, offset, 7276, 7307, GREEN_COLOR, TICKER, False)
    assert isinstance(r, dict)
    assert 'qty' in r
    assert 'init_price' in r
    assert 'stop_price' in r
    assert 'take_price' in r
    assert 'order_uid' in r
    assert 'response' in r
    assert 'orderID' in r['response']
    assert r['response']['orderID']


def test_order_size_red():
    r = place_order_init(offset, offset, 8701, 8787, RED_COLOR, TICKER, True)
    assert r['init_price'] == 8700
    assert r['stop_price'] == 8788
    assert r['qty'] == -86


def test_order_size_green():
    r = place_order_init(offset, offset, 8613, 8699, GREEN_COLOR, TICKER, True)
    assert r['init_price'] == 8700
    assert r['stop_price'] == 8612
    assert r['qty'] == 84


def test_order_saved_to_storage():
    r = place_order_init(offset, offset, 8613, 8699, GREEN_COLOR, TICKER, True)
    assert r['take_price'] == 8785.
    assert r['stop_price'] == 8612.

    saved_row = get_init_order(r['order_uid'])
    assert saved_row['take'] == '8785'
    assert saved_row['stop'] == '8612.0'
    assert saved_row['color'] == GREEN_COLOR
    assert saved_row['qty'] == '84.0'

    order_not_found = get_init_order('unknown order')
    assert order_not_found is None




