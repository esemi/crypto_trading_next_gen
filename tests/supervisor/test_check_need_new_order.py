from app.configs import RED_COLOR, GREEN_COLOR, TICKER
from app.supervisor import check_need_new_order


def test_valid_response():
    r = check_need_new_order(TICKER)
    if not r:
        assert r is None
    else:
        assert isinstance(r, dict)
        assert 'low_price' in r
        assert 'high_price' in r
        assert 'color' in r
        assert r['color'] in {RED_COLOR, GREEN_COLOR}


def test_invalid_ticker():
    r = check_need_new_order('INVALID_TICKER')
    assert r is None
