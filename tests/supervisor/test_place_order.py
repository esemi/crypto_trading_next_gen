from configs import RED_COLOR, GREEN_COLOR, TICKER, INIT_ORDER_PRICE_OFFSET
from crypto_bot.supervisor import place_order


def test_success_green():
    r = place_order(10, 15, GREEN_COLOR, TICKER)
    assert isinstance(r, dict)
    assert 'qty' in r
    assert 'price' in r
    assert 'client_uid' in r
    assert 'response' in r
    assert r['qty'] > 0.
    assert r['price'] == 15 + INIT_ORDER_PRICE_OFFSET
    assert r['client_uid']
    assert r['response']


def test_success_red():
    r = place_order(10, 15, RED_COLOR, TICKER)
    assert isinstance(r, dict)
    assert 'qty' in r
    assert 'price' in r
    assert 'client_uid' in r
    assert 'response' in r
    assert r['qty'] < 0.
    assert r['price'] == 10 - INIT_ORDER_PRICE_OFFSET
    assert r['client_uid']
    assert r['response']
