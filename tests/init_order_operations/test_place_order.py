from app.configs import RED_COLOR, GREEN_COLOR, TICKER
from app.storage import get_init_order
from app.init_order_operations import place_order_init

offset = 2.


def test_small_bucket():
    r = place_order_init(5, 5, 5, 5, 10, 15, GREEN_COLOR, TICKER, True)
    assert r is None


def test_success_green():
    """
    Long order

    """

    r = place_order_init(offset, offset, offset, offset, 10, 15, GREEN_COLOR, TICKER, True)
    assert isinstance(r, dict)
    assert 'qty' in r
    assert 'init_price' in r
    assert 'stop_price' in r
    assert 'take_price' in r
    assert 'order_uid' in r
    assert 'response' in r
    assert r['order_uid']
    assert r['response']


def test_success_red():
    """
    Short order

    """

    r = place_order_init(offset, offset, offset, offset, 10, 15, RED_COLOR, TICKER, True)
    assert isinstance(r, dict)
    assert 'qty' in r
    assert 'init_price' in r
    assert 'stop_price' in r
    assert 'take_price' in r
    assert 'order_uid' in r
    assert 'response' in r
    assert r['order_uid']
    assert r['response']


def test_real_place_order():
    r = place_order_init(offset, offset, offset, offset, 7276, 7307, GREEN_COLOR, TICKER, False)
    assert isinstance(r, dict)
    assert 'qty' in r
    assert 'init_price' in r
    assert 'stop_price' in r
    assert 'take_price' in r
    assert 'order_uid' in r
    assert 'response' in r
    assert 'orderID' in r['response']
    assert r['response']['orderID']


def test_order_saved_to_storage():
    r = place_order_init(offset, offset, offset, offset, 8613, 8699, GREEN_COLOR, TICKER, True)

    saved_row = get_init_order(r['order_uid'])
    assert 'take' in saved_row
    assert 'stop' in saved_row
    assert 'color' in saved_row
    assert saved_row['color'] == GREEN_COLOR
    assert 'qty' in saved_row

    order_not_found = get_init_order('unknown order')
    assert order_not_found is None




