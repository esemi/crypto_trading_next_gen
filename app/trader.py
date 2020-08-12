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


import argparse
import logging
import signal
import sys
import time
from datetime import datetime

from bitmex_ws import connect
from clearing_operations import fetch_orders_for_clearing, clear_order
from configs import TICKER, INIT_ORDER_PRICE_OFFSET, STOP_ORDER_PRICE_OFFSET, TAKE_ORDER_PRICE_OFFSET, \
    INIT_ORDER_TIME_OFFSET, CLEARING_TIME_OFFSET
from event_driven_operations import proceed_event
from init_order_operations import check_need_new_order, place_order_init, OrderProperties

KEYBOARD_INTERRUPT = False
INTERRUPT_SAFE = False
WS_CLIENT = None


def pretty_log(message: str, start: bool = True):
    def __log_empty_rows():
        for i in range(4):
            logging.info('')

    if start:
        __log_empty_rows()
        logging.info(message)
    else:
        logging.info(message)
        __log_empty_rows()


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

    init_order_start_time = datetime.now().replace(minute=0, second=20, microsecond=0)
    clearing_start_time = datetime.now().replace(minute=2, second=0, microsecond=0)

    events_processed = 0
    while True:

        # clearing by timer
        clearing_process_timer = (datetime.now() - clearing_start_time).total_seconds()
        logging.debug(f'check clearing time needed {clearing_process_timer=}')
        if clearing_process_timer >= CLEARING_TIME_OFFSET:
            pretty_log('clearing start', True)
            clearing_start_time = datetime.now().replace(minute=2, second=0, microsecond=0)
            for order_uid in fetch_orders_for_clearing():
                logging.info(f'clear order {order_uid}')
                clear_order(order_uid)
            pretty_log('clearing end', False)

        # post init order every hour
        init_order_process_timer = (datetime.now() - init_order_start_time).total_seconds()
        logging.debug(f'check init order needed {init_order_process_timer=}')
        if init_order_process_timer >= INIT_ORDER_TIME_OFFSET:
            pretty_log('init new order start', True)
            init_order_start_time = datetime.now().replace(minute=0, second=20, microsecond=0)
            order_props: OrderProperties = check_need_new_order(TICKER)
            logging.info(f'check need new order {order_props}')
            if order_props:
                INTERRUPT_SAFE = True
                order = place_order_init(init_price_offset=INIT_ORDER_PRICE_OFFSET,
                                         stop_price_offset=STOP_ORDER_PRICE_OFFSET,
                                         take_price_offset=TAKE_ORDER_PRICE_OFFSET,
                                         take_price_factor=order_props.take_profit_factor,
                                         clearing_offset=order_props.clearing_interval,
                                         candle=order_props.candle,
                                         ticker=TICKER)
                logging.info(f'place new init order {order}')
                INTERRUPT_SAFE = False
            pretty_log('init new order end', False)

        # post profit orders by filled event
        while True:
            if WS_CLIENT.exited:
                logging.warning('reconnect to socket')
                WS_CLIENT = connect()

            current_event = WS_CLIENT.get_event()
            if not current_event:
                break

            pretty_log('process event start', True)
            INTERRUPT_SAFE = True
            events_processed += 1
            event_processing_result = proceed_event(current_event['uid'])
            INTERRUPT_SAFE = False
            pretty_log(f'end process {event_processing_result=}', False)

        time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='crypto trader')
    parser.add_argument('--debug', type=bool,  help='Show more logs', default=False)
    params = parser.parse_args()
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        level=logging.DEBUG if params.debug else logging.INFO,
                        datefmt='%Y-%m-%d %H:%M:%S')
    pretty_log('start trader process', True)
    main()
    pretty_log('end trader process', False)
