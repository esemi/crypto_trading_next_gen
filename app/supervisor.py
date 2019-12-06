#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт запускается раз в час
- чистит протухшие заявки и выставляет новые;
- определяет, нужно ли выставлять новый ордер в зависимости от 3х последних часовых свечей;
- если нужно - считает параметры тейка/стопа, записывает новую строчку в лист ожидания и выставляет ордер.

"""

import logging
import math
from typing import Optional

from bitmex_rest import get_buckets, post_stop_order
from configs import (TICKER, RED_COLOR, GREEN_COLOR, INIT_ORDER_PRICE_OFFSET, INIT_ORDER_SIZE_IN_BTC,
                     STOP_ORDER_PRICE_OFFSET, TAKE_ORDER_PRICE_OFFSET)
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
        if force:
            return prepared_buckets[0]

        if prepared_buckets[0]['color'] != prepared_buckets[1]['color'] and \
                prepared_buckets[1]['color'] == prepared_buckets[2]['color']:
            return prepared_buckets[0]
    return


def place_order_init(init_price_offset: float, stop_price_offset: float, take_price_offset: float, low_price: float,
                     high_price: float, color: str, ticker: str, dry_run: bool = False) -> Optional[dict]:
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
        init_price = low_price - init_price_offset
        stop_price = high_price + stop_price_offset
        take_price = low_price - bucket_size - take_price_offset

    else:
        # long order
        side_factor = 1.
        init_price = high_price + init_price_offset
        stop_price = low_price - stop_price_offset
        take_price = high_price + bucket_size + take_price_offset

    logging.info(f'place order: side_factor={side_factor} init_price={init_price} stop_price_offset={stop_price_offset}'
                 f' bucket_size={bucket_size} stop={stop_price} take={take_price}')

    # compute order size
    qty = math.floor(
        INIT_ORDER_SIZE_IN_BTC / (1 / min(init_price, stop_price) - 1 / max(init_price, stop_price))
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
        response = post_stop_order(ticker, qty, init_price, order_uid, comment='Init order by supervisor.py')
        logging.info(f'post order to exchange resp={response}')

    return {
        'qty': qty,
        'init_price': init_price,
        'stop_price': stop_price,
        'take_price': take_price,
        'order_uid': order_uid,
        'response': response
    }


def main(ticker: str, force_entry: bool = False):
    # todo infinite loop ?

    # todo clearing oldest orders (12h alive)

    # check need new order
    bucket = check_need_new_order(ticker, force_entry)
    logging.info(f'check need new order {bucket}')
    if not bucket:
        return

    order = place_order_init(init_price_offset=INIT_ORDER_PRICE_OFFSET, stop_price_offset=STOP_ORDER_PRICE_OFFSET,
                             take_price_offset=TAKE_ORDER_PRICE_OFFSET, ticker=ticker, **bucket)
    logging.info(f'place new order {order}')
    if not order:
        return


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S')

    logging.info('start supervisor process--------------------------------------------')
    main(TICKER)
    logging.info('end supervisor process--------------------------------------------')
