#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт подписывается на события изменения ордеров и реагирует только на них

Служит затем, чтобы оперативно выставлять/снимать заявки тейка/стопа

"""
import logging
import signal
import sys
import time

from bitmex_api import client_ws
from configs import TICKER
from storage import get_init_order, get_profit_order

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


def main(ticker: str):
    global INTERRUPT_SAFE

    signal.signal(signal.SIGINT, sigint_handler)

    events_processed = 0
    for current_event in client_ws.iter_events():
        INTERRUPT_SAFE = True
        logging.info('start process event--------------------------------------------')
        logging.info(f'fetch new order event {current_event}')
        events_processed += 1

        init_order_info = get_init_order(current_event['uid'])
        profit_order = get_profit_order(current_event['uid'])

        logging.info(f'fetch orders by event init={init_order_info} profit={profit_order}')
        if init_order_info:
            # todo save stop and take orders to db
            # todo place stop and take orders
            # todo rm init order from storage
            pass

        elif profit_order:
            # todo cancel pair order
            # todo rm stop and take orders from db
            pass

        else:
            logging.error('NOT FOUND ORDER INTO STORAGE!')

        INTERRUPT_SAFE = False
        logging.info('end process event')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S')

    logging.info('start trader process')
    main(TICKER)
    logging.info('end trader process')
