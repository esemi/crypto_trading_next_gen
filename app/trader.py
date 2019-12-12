#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Трейдер скрипт

- чистит протухшие заявки и выставляет новые;
- определяет, нужно ли выставлять новый ордер в зависимости от 3х последних часовых свечей;
- если нужно - считает параметры тейка/стопа, записывает новую строчку в лист ожидания и выставляет ордер.
- слушает изменения своих ордеров по сокету и оперативно выставляет стоп/тейк заявки при исполнении входного ордера
- снимает парный сто/тейк при исполнении одного из них

"""

import logging
import signal
import sys
import time
from datetime import datetime

from bitmex_ws import connect
from configs import TICKER, INIT_ORDER_PRICE_OFFSET, STOP_ORDER_PRICE_OFFSET, TAKE_ORDER_PRICE_OFFSET
from event_driven_operations import proceed_event
from init_order_operations import check_need_new_order, place_order_init

KEYBOARD_INTERRUPT = False
INTERRUPT_SAFE = False
WS_CLIENT = None


def sigint_handler(signal, frame):
    global KEYBOARD_INTERRUPT, INTERRUPT_SAFE, WS_CLIENT
    logging.warning(f'handle interrupt sig {signal} {INTERRUPT_SAFE}')
    if INTERRUPT_SAFE:
        KEYBOARD_INTERRUPT = True
    else:
        if WS_CLIENT:
            WS_CLIENT.exit()
        sys.exit(0)


def main():
    global INTERRUPT_SAFE, WS_CLIENT
    WS_CLIENT = connect()

    signal.signal(signal.SIGINT, sigint_handler)

    init_order_start_time = datetime.now().replace(minute=1, second=0, microsecond=0)

    events_processed = 0
    while True:

        # auto reconnect to wss
        if WS_CLIENT.exited:
            logging.warning('reconnect to socket')
            WS_CLIENT.exit()
            WS_CLIENT = connect()

        # post init order every hour
        current_time = datetime.now()
        offset_in_seconds = (current_time - init_order_start_time).total_seconds()
        logging.debug(f'check init order needed {init_order_start_time} {current_time} offset={offset_in_seconds}')
        if offset_in_seconds >= 3600:
            init_order_start_time = datetime.now().replace(minute=1, second=0, microsecond=0)
            bucket = check_need_new_order(TICKER)
            logging.info(f'check need new order {bucket}')
            if bucket:
                INTERRUPT_SAFE = True
                order = place_order_init(init_price_offset=INIT_ORDER_PRICE_OFFSET,
                                         stop_price_offset=STOP_ORDER_PRICE_OFFSET,
                                         take_price_offset=TAKE_ORDER_PRICE_OFFSET, ticker=TICKER, **bucket)
                logging.info(f'place new init order {order}')
                INTERRUPT_SAFE = False

        # post profit orders by filled event
        while True:
            current_event = WS_CLIENT.get_event()
            if not current_event:
                break

            logging.info('start process event--------------------------------------------')
            INTERRUPT_SAFE = True
            events_processed += 1
            res = proceed_event(current_event['uid'])
            INTERRUPT_SAFE = False
            logging.info(f'end process event={res}---------------------------------------------------')

        time.sleep(1)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')
    logging.info('start trader process')
    main()
    logging.info('end trader process')
