#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from bitmex_rest import get_buckets, post_stop_limit_order
from configs import (RED_COLOR, GREEN_COLOR, INIT_ORDER_SIZE_IN_BTC, INIT_ORDER_TRIGGER_PRICE_OFFSET,
                     INIT_ORDER_FILTERS, CandleFilter)
from storage import add_init_order, gen_uid


@dataclass
class CandleItem:
    low: float
    high: float
    open: float
    close: float
    color: str

    @property
    def size(self) -> float:
        """Размер свечи"""
        return self.high - self.low

    @property
    def percent_size_of_cost(self) -> float:
        """Процент размера свечи от цены закрытия"""
        return (self.size / self.close) * 100.

    @property
    def percent_size_of_body(self) -> float:
        """Процент тела свечи"""
        return abs(self.open - self.close) / self.size


@dataclass
class OrderProperties:
    candle: CandleItem
    take_profit_factor: float = 0.
    clearing_interval: int = 3600


def check_need_new_order(ticker: str, force: bool = False) -> Optional[OrderProperties]:
    """
    Если две старшие свечи отличаются по цвету от самой свежей - тогда вписываемся в сделку
    Возвращает словарь с данными свечки для входа или None, если входа нет

    """

    source_buckets = get_buckets(ticker, 3)
    logging.info(f'fetch buckets {source_buckets}')

    if [i for i in source_buckets if i['open'] == i['close']]:
        logging.info('skip by found empty buckets')
        return

    candles = [CandleItem(low=i['low'], high=i['high'], close=i['close'], open=i['open'],
                          color=(GREEN_COLOR if i['open'] < i['close'] else RED_COLOR))
               for i in list(source_buckets)]
    logging.info(f'prepare candles {candles}')

    if not candles:
        logging.info('candles not found')
        return

    first_candle: CandleItem = candles.pop()
    second_candle: CandleItem = candles.pop()
    last_candle: CandleItem = candles.pop()

    order = OrderProperties(candle=last_candle)
    if force:
        logging.info(f'force select candle {last_candle}')
        return order

    # Фильтруем по цвету - комбо для входа red-green-green or green-red-red
    if last_candle.color == second_candle.color or second_candle.color != first_candle.color:
        logging.info(f'skip by colors {first_candle=} {second_candle=} {last_candle=}')
        return

    logging.info(f'{last_candle=}')
    for filter_config in INIT_ORDER_FILTERS:
        logging.info(f'apply filters to candles {filter_config=}')

        if not _apply_filter_candle(last_candle, filter_config.last_candle):
            logging.info(f'skip by {last_candle} and {filter_config.last_candle}')
            continue

        if not _apply_filter_candle(second_candle, filter_config.second_candle):
            logging.info(f'skip by {second_candle} and {filter_config.second_candle}')
            continue

        if not _apply_filter_candle(first_candle, filter_config.first_candle):
            logging.info(f'skip by {first_candle} and {filter_config.first_candle}')
            continue

        order.clearing_interval = filter_config.clearing_interval
        order.take_profit_factor = filter_config.take_profit_factor
        logging.info(f'hit candle {order=}')
        return order

    logging.info('not found applicable config for candle')
    return


def _apply_filter_candle(candle: CandleItem, filters_config: Optional[CandleFilter]) -> bool:
    logging.info(f'apply filter {filters_config} to {candle=}')

    if filters_config and filters_config.size:
        if not (filters_config.size.min <= candle.percent_size_of_cost <= filters_config.size.max):
            return False

    if filters_config and filters_config.body:
        if not (filters_config.body.min <= candle.percent_size_of_body <= filters_config.body.max):
            return False

    return True


def place_order_init(init_price_offset: float, stop_price_offset: float, take_price_offset: float,
                     take_price_factor: float, clearing_offset: int, candle: CandleItem, ticker: str,
                     dry_run: bool = False) -> Optional[dict]:
    logging.info(
        f'place order: start {candle=} {ticker=} price_offset={init_price_offset}')

    # compute order price
    if candle.size <= init_price_offset:
        logging.warning(f'too small bucket={candle.size} - skip order')
        return

    if candle.color == RED_COLOR:
        # short order
        side_factor = 1
        init_order_price = candle.low - init_price_offset
        init_trigger_price = candle.low - INIT_ORDER_TRIGGER_PRICE_OFFSET
        stop_price = candle.high + stop_price_offset
        take_price = candle.low - (candle.size * take_price_factor) - take_price_offset

    else:
        # long order
        side_factor = -1
        init_order_price = candle.high + init_price_offset
        init_trigger_price = candle.high + INIT_ORDER_TRIGGER_PRICE_OFFSET
        stop_price = candle.low - stop_price_offset
        take_price = candle.high + (candle.size * take_price_factor) + take_price_offset

    logging.info(f'place order: {side_factor=} {init_trigger_price=} {init_order_price=} '
                 f'{stop_price_offset=} {candle.size=} {stop_price=} {take_price=}')

    init_order_price = Decimal(init_order_price)
    init_trigger_price = Decimal(init_trigger_price)
    stop_price = Decimal(stop_price)
    take_price = Decimal(take_price)

    logging.info(f'place order round: {side_factor=} {init_trigger_price=} {init_order_price=} '
                 f'{stop_price_offset=} {candle.size=} {stop_price=} {take_price=}')

    # compute order size
    qty = round(INIT_ORDER_SIZE_IN_BTC / (
                (min(init_trigger_price, stop_price) - max(init_trigger_price, stop_price)) * Decimal('0.000001')))
    qty: int = qty * side_factor

    logging.info(f'place order: compute qty={qty}')

    order_uid = gen_uid()
    r = add_init_order(order_uid, stop_price, take_price, abs(qty), candle.color, ticker, clearing_offset)
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
