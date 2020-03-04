from app.init_order_operations import check_need_new_order


def test_invalid_ticker():
    r = check_need_new_order('INVALID_TICKER')
    assert r is None
