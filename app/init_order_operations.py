#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import math
from typing import Optional

from bitmex_rest import get_buckets, post_stop_limit_order
from configs import (RED_COLOR, GREEN_COLOR, INIT_ORDER_SIZE_IN_BTC, INIT_ORDER_BUCKET_SIZE_INTERVAL)
from storage import add_init_order, gen_uid


def check_need_new_order(ticker: str, force: bool = False) -> Optional[dict]:
    """
    Если две старшие свечи отличаются по цвету от самой свежей - тогда вписываемся в сделку
    Возвращает словарь с данными свечки для входа или None, если входа нет

    """

    last_buckets = get_buckets(ticker, 3)
    logging.info(f'fetch buckets {last_buckets}')

    prepared_buckets = [{
        'low_price': i['low'],
        'high_price': i['high'],
        'color': GREEN_COLOR if i['open'] <= i['close'] else RED_COLOR
    } for i in list(last_buckets)]
    logging.info(f'prepare buckets {prepared_buckets}')

    if last_buckets:
        last_bucket = prepared_buckets[0]
        if force:
            return last_bucket

        bucket_size = last_bucket['high_price'] - last_bucket['low_price']
        logging.info(f'{bucket_size=} (allowed {INIT_ORDER_BUCKET_SIZE_INTERVAL})')

        if INIT_ORDER_BUCKET_SIZE_INTERVAL[0] and bucket_size < INIT_ORDER_BUCKET_SIZE_INTERVAL[0]:
            logging.warning(f'skip bucket by {bucket_size=} too small')
            return
        if INIT_ORDER_BUCKET_SIZE_INTERVAL[1] and bucket_size > INIT_ORDER_BUCKET_SIZE_INTERVAL[1]:
            logging.warning(f'skip bucket by {bucket_size=} too big')
            return

        if last_bucket['color'] != prepared_buckets[1]['color'] and \
                prepared_buckets[1]['color'] == prepared_buckets[2]['color']:
            return last_bucket
    return


def place_order_init(init_price_offset: float, stop_price_offset: float, take_price_offset: float,
                     take_price_factor: float, low_price: float, high_price: float, color: str, ticker: str,
                     dry_run: bool = False) -> Optional[dict]:
    logging.info(
        f'place order: start low={low_price} high={high_price} {color} {ticker} price_offset={init_price_offset}')

    # compute order price
    bucket_size = high_price - low_price
    if bucket_size <= init_price_offset:
        logging.warning(f'too small bucket={bucket_size} - skip order')
        return

    if color == RED_COLOR:
        # short order
        side_factor = -1.
        init_order_price = low_price - init_price_offset
        init_trigger_price = low_price
        stop_price = high_price + stop_price_offset
        take_price = low_price - (bucket_size * take_price_factor) - take_price_offset

    else:
        # long order
        side_factor = 1.
        init_order_price = high_price + init_price_offset
        init_trigger_price = high_price
        stop_price = low_price - stop_price_offset
        take_price = high_price + (bucket_size * take_price_factor) + take_price_offset

    logging.info(f'place order: {side_factor=} {init_trigger_price=} {init_order_price=} '
                 f'{stop_price_offset=} {bucket_size=} {stop_price=} {take_price=}')

    # compute order size
    qty = math.floor(
        INIT_ORDER_SIZE_IN_BTC / (1 / min(init_trigger_price, stop_price) - 1 / max(init_trigger_price, stop_price))
    ) * side_factor
    logging.info(f'place order: compute qty={qty}')

    order_uid = gen_uid()
    r = add_init_order(order_uid, stop_price, take_price, abs(qty), color, ticker)
    logging.info(f'place order: save order to db {order_uid}; response={r}')

    response = 'dry run'
    if not dry_run:
        if abs(qty) < 1:
            logging.warning(f'too small qty computed={qty} - skip order')
            return
        response = post_stop_limit_order(ticker, qty, init_trigger_price, init_order_price, order_uid,
                                         comment='Init order by supervisor.py')
        logging.info(f'post order to exchange resp={response}')

    return {
        'qty': qty,
        'init_price': init_trigger_price,
        'stop_price': stop_price,
        'take_price': take_price,
        'order_uid': order_uid,
        'response': response
    }
