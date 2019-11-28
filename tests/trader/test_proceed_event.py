from storage import add_init_order, get_init_order, get_profit_order, client_redis, _profit_order_key
from trader import proceed_event


def test_proceed_unknown_order():
    resp = proceed_event('unknown_order_uid', True)
    assert resp == 'not found order'


def test_proceed_init_order():
    client_redis.flushall()

    init_uid = 'init_order_uid'
    add_init_order(init_uid, 100, 200)

    resp = proceed_event(init_uid, True)
    assert resp == 'proceed init order'
    assert get_init_order(init_uid) is None

    profit_keys = client_redis.keys(_profit_order_key('*'))
    assert len(profit_keys) == 2
    first_order = client_redis.hgetall(profit_keys[0])['pair_uid']
    second_order = client_redis.hgetall(profit_keys[1])['pair_uid']
    assert get_profit_order(first_order) == second_order
    assert get_profit_order(second_order) == first_order


def test_proceed_init_order_real():
    client_redis.flushall()

    init_uid = 'init_order_uid'
    add_init_order(init_uid, 100, 200)

    resp = proceed_event(init_uid, False)
    assert resp == 'proceed init order'
