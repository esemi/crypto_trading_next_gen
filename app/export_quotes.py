#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""
Экспорт котировок по ETH и BTC парам за последний год

- часовые свечи по двум парам
- дневные свечи по ним же

"""
import argparse
import logging
import time
from datetime import datetime

from bitmex_rest import get_buckets


def main(ticker: str, limit_days: int, bin_size: str):
    print('date;ticker;high;low;open;close')
    total_rows = 0
    offset = 0
    if bin_size == '1h':
        limit_rows = limit_days * 24
    else:
        limit_rows = limit_days

    while total_rows < limit_rows:
        r = get_buckets(ticker, 1000, offset, bin_size)
        logging.info(f'response {r=}')
        offset += 1000
        total_rows += len(r)
        for i in r:
            dt: datetime = i.get("timestamp")
            print(f"{dt.isoformat()};{i.get('symbol')};{i.get('high')};{i.get('low')};{i.get('open')};{i.get('close')}")

        if not len(r):
            logging.warning('empty reply from API')
            break
        time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='crypto export quotes')
    parser.add_argument('--ticker', type=str,  help='Ticker for export (example: ETHUSD)', required=True)
    parser.add_argument('--days', type=int,  help='Quotes for {days} old', required=True)
    parser.add_argument('--bin', type=str,  help='1h or 1d bin', required=True)
    params = parser.parse_args()
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')
    logging.info(f'start fetch {params.ticker} quotes')
    main(params.ticker, params.days, params.bin)
    logging.info(f'end fetch {params.ticker} quotes')
