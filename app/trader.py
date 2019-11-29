#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт подписывается на события изменения ордеров и реагирует только на них

Служит затем, чтобы оперативно выставлять/снимать заявки тейка/стопа

"""
import logging
import signal
import sys

from .bitmex_api import client_ws
from configs import TICKER
from .storage import get_init_order, get_profit_order, gen_uid, add_profit_order, del_init_order, del_profit_order

KEYBOARD_INTERRUPT = False
INTERRUPT_SAFE = False


def sigint_handler(signal, frame):
    global KEYBOARD_INTERRUPT, INTERRUPT_SAFE
    logging.warning(f'handle interrupt sig {signal} {INTERRUPT_SAFE}')
    if INTERRUPT_SAFE:
        KEYBOARD_INTERRUPT = True
    else:
        client_ws.exit()
        sys.exit(0)


def proceed_event(current_event_uid: str, dry_run: bool = False) -> str:
    logging.info(f'fetch new order event {current_event_uid}')

    init_order_info = get_init_order(current_event_uid)
    profit_order_paid_uid = get_profit_order(current_event_uid)
    logging.info(f'fetch orders by event init={init_order_info} profit_pair={profit_order_paid_uid}')

    if init_order_info:
        logging.info('process init order filled')

        # save stop and take orders to db
        stop_uid = gen_uid()
        take_uid = gen_uid()
        add_profit_order(stop_uid, take_uid, current_event_uid)
        add_profit_order(take_uid, stop_uid, current_event_uid)
        logging.info(f'save profit orders to storage stop={stop_uid} take={take_uid}')

        if not dry_run:
            # todo place stop and take orders
            pass

        # rm init order from storage
        del_init_order(current_event_uid)
        logging.info(f'rm init order from db {current_event_uid}')

        return 'proceed init order'

    elif profit_order_paid_uid:
        logging.info('process profit order filled')

        if not dry_run:
            # todo cancel pair order
            pass

        # rm stop and take orders from db
        del_profit_order(current_event_uid)
        del_profit_order(profit_order_paid_uid)

    else:
        logging.error('NOT FOUND ORDER INTO STORAGE!')
        return 'not found order'


def main(ticker: str):
    global INTERRUPT_SAFE

    signal.signal(signal.SIGINT, sigint_handler)

    events_processed = 0
    for current_event in client_ws.iter_events():
        logging.info('start process event--------------------------------------------')
        INTERRUPT_SAFE = True
        events_processed += 1
        res = proceed_event(current_event['uid'])
        INTERRUPT_SAFE = False
        logging.info(f'end process event={res}---------------------------------------------------')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S')

    logging.info('start trader process')
    main(TICKER)
    logging.info('end trader process')
