#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time

from bravado.exception import HTTPServerError

from bitmex_rest import post_limit_order, cancel_order, post_stop_order
from configs import GREEN_COLOR, LIMIT_CALL_TRIES, LIMIT_CALL_TIMEOUT
from storage import get_init_order, get_profit_order, gen_uid, add_profit_order, del_init_order, del_profit_order


def proceed_event(current_event_uid: str, dry_run: bool = False) -> str:
    logging.info(f'fetch new order event {current_event_uid}')

    init_order_info = get_init_order(current_event_uid)
    profit_order_pair_uid = get_profit_order(current_event_uid)
    logging.info(f'fetch orders by event init={init_order_info} profit_pair={profit_order_pair_uid}')

    if init_order_info:
        logging.info('process init order filled')

        # save stop and take orders to db
        stop_uid = gen_uid()
        take_uid = gen_uid()
        add_profit_order(stop_uid, take_uid, current_event_uid)
        add_profit_order(take_uid, stop_uid, current_event_uid)
        logging.info(f'save profit orders to storage stop={stop_uid} take={take_uid}')

        orders_resp = place_orders_profit(**init_order_info, dry_run=dry_run, stop_uid=stop_uid, take_uid=take_uid)
        logging.info(f'place profit orders={orders_resp}')

        # rm init order from storage
        del_init_order(current_event_uid)
        logging.info(f'rm init order from db {current_event_uid}')

        return 'proceed init order'

    elif profit_order_pair_uid:
        logging.info('process profit order filled')

        # cancel pair order
        if not dry_run:
            cancel_resp = cancel_order(profit_order_pair_uid, comment='Cancel order by trader.py')
            logging.info(f'cancel order={profit_order_pair_uid} {cancel_resp}')

        # rm stop and take orders from db
        del_profit_order(current_event_uid)
        del_profit_order(profit_order_pair_uid)
        return 'proceed profit order'

    else:
        logging.warning('NOT FOUND ORDER INTO STORAGE!')
        return 'not found order'


def place_orders_profit(take: float, stop: float, qty: float, color: str, ticker: str, stop_uid: str, take_uid: str,
                        dry_run: bool = False) -> dict:

    take_price = float(take)
    stop_price = float(stop)
    qty = float(qty)
    logging.info(f'place profit orders take_price={take_price}, stop_price={stop_price}, qty={qty}, color={color}, '
                 f'ticker={ticker} {stop_uid} {take_uid}')

    if color == GREEN_COLOR:
        qty *= -1.

    stop_resp = take_resp = 'dry run'

    logging.info(f'place stop order {ticker}: qty={qty}, stop_price={stop_price}, stop_uid={stop_uid}')
    if not dry_run:
        try_num = 0
        while True:
            try_num += 1
            try:
                stop_resp = post_stop_order(ticker, qty, stop_price, stop_uid, comment='Stop order by trader.py')
                logging.info(f'exchange resp for stop order={stop_resp}')
                break
            except HTTPServerError as e:
                logging.info(f'exchange exception={e}')
                if try_num < LIMIT_CALL_TRIES:
                    time.sleep(LIMIT_CALL_TIMEOUT)
                else:
                    raise e

    logging.info(f'place limit order {ticker}: qty={qty}, price={take_price}, take_uid={take_uid}')
    if not dry_run:
        try_num = 0
        while True:
            try_num += 1
            try:
                take_resp = post_limit_order(ticker, qty, take_price, take_uid, comment='Profit order by trader.py')
                logging.info(f'exchange resp for take profit order={take_resp}')
                break
            except HTTPServerError as e:
                logging.info(f'exchange exception={e}')
                if try_num < LIMIT_CALL_TRIES:
                    time.sleep(LIMIT_CALL_TIMEOUT)
                else:
                    raise e

    return dict(
        stop=dict(
            response=stop_resp,
            qty=qty,
            uid=stop_uid,
            price=stop_price
        ),
        take=dict(
            response=take_resp,
            qty=qty,
            uid=take_uid,
            price=take_price
        )
    )
