from configs import RED_COLOR, GREEN_COLOR, TICKER
from crypto_bot.bitmex_api import init_client
from crypto_bot.supervisor import place_order

offset = 1.


def test_success_green():
    r = place_order(offset, 10, 15, GREEN_COLOR, TICKER, True)
    assert isinstance(r, dict)
    assert 'qty' in r
    assert 'price' in r
    assert 'client_uid' in r
    assert 'response' in r
    assert r['qty'] > 0.
    assert r['price'] == 15 + offset
    assert r['client_uid']
    assert r['response']


def test_success_red():
    r = place_order(offset, 10, 15, RED_COLOR, TICKER, True)
    assert isinstance(r, dict)
    assert 'qty' in r
    assert 'price' in r
    assert 'client_uid' in r
    assert 'response' in r
    assert r['qty'] < 0.
    assert r['price'] == 10 - offset
    assert r['client_uid']
    assert r['response']


def test_real_place_order():
    # init_client(False)
    r = place_order(offset, 10, 15, GREEN_COLOR, TICKER, False)
    # init_client(True)
    assert isinstance(r, dict)
    assert 'qty' in r
    assert 'price' in r
    assert 'client_uid' in r
    assert 'response' in r
    assert r['qty'] > 0.
    assert r['price'] == 15 + offset
    assert r['client_uid']
    assert r['response']
    print(r)
