#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт запускается раз в час
- чистит протухшие заявки и выставляет новые;
- определяет, нужно ли выставлять новый ордер в зависимости от 3х последних часовых свечей;
- если нужно - считает параметры тейка/стопа, записывает новую строчку в лист ожидания и выставляет ордер.

"""

import logging
import uuid
from typing import Optional

from configs import TICKER, RED_COLOR, GREEN_COLOR, INIT_ORDER_PRICE_OFFSET
from crypto_bot.bitmex_api import get_buckets, post_order


def check_need_new_order(ticker: str) -> Optional[dict]:
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
    } for i in list(last_buckets) if i['open'] != i['close']]
    logging.info(f'prepare buckets {prepared_buckets}')

    if last_buckets:
        if prepared_buckets[0]['color'] != prepared_buckets[1]['color'] and \
                prepared_buckets[1]['color'] == prepared_buckets[2]['color']:
            return prepared_buckets[0]
    return


def place_order(price_offset: float, low_price: float, high_price: float, color: str, ticker: str, dry_run: bool = False) -> dict:
    logging.info(f'place order: start {low_price} {high_price} {color} {ticker} {price_offset}')

    side_factor = -1. if color == RED_COLOR else 1.
    price = (low_price if color == RED_COLOR else high_price) + (side_factor * price_offset)
    logging.info(f'place order: price={price}')

    # todo compute order size
    qty = 1. * side_factor
    logging.info(f'place order: qty={qty}')

    # todo save new order to db for get client_uid
    order_uid = uuid.uuid4().hex
    logging.info(f'place order: save order to db {order_uid}')

    response = 'dry run'
    if not dry_run:
        response = post_order(ticker, qty, price, order_uid)
        logging.info(f'post order to exchange resp={response}')

    return {
        'qty': qty,
        'price': price,
        'client_uid': 'todo',
        'response': response
    }


def main(ticker: str):
    # todo infinite loop ?

    # todo clear db?

    # todo clearing oldest orders

    # check need new order
    bucket = check_need_new_order(ticker)
    logging.info(f'check need new order {bucket}')
    if not bucket:
        return

    # todo place new order and save TP/SL config for trader.py
    order = place_order(price_offset=INIT_ORDER_PRICE_OFFSET, ticker=ticker, **bucket)
    logging.info(f'place new order {order}')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')

    logging.info('start supervisor process--------------------------------------------')
    main(TICKER)
    logging.info('end supervisor process--------------------------------------------')

