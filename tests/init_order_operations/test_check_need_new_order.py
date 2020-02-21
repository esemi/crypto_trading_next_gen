from datetime import datetime

from app.configs import TICKER
from app.init_order_operations import check_need_new_order
from bitmex_rest import get_buckets


def test_invalid_ticker():
    r = check_need_new_order('INVALID_TICKER')
    assert r is None


def test_export_quotes():
    limit_days = 400
    with open('/tmp/ethusd.csv', 'w') as fd:
        fd.write("date;open;close\n")
        total_rows = 0
        offset = 0
        while total_rows < limit_days*24:
            r = get_buckets(TICKER, 1000, offset)
            offset += 1000
            total_rows += len(r)
            for i in r:
                dt: datetime = i.get("timestamp")
                fd.write(f"{dt.isoformat()};{i.get('open')};{i.get('close')}\n")
