import json
from typing import Optional

import bitmex
from bravado.exception import HTTPNotFound

from configs import TEST_MODE, API_KEY, API_SECRET


def get_self_orders() -> Optional[list]:
    return client_rest.Order.Order_getOrders(filter=json.dumps({'open': True})).result()[0]


def get_buckets(ticker: str, count: int, start: int = 0) -> list:
    return client_rest.Trade.Trade_getBucketed(binSize='1h', partial=False, symbol=ticker, count=count, start=start,
                                               reverse=True).result()[0]


def post_stop_limit_order(ticker: str, qty: float, trigger_price: float, order_price: float, order_uid: str, comment: str = '') -> dict:
    return client_rest.Order.Order_new(symbol=ticker, orderQty=qty, ordType='StopLimit', stopPx=trigger_price,
                                       execInst='LastPrice', price=order_price,
                                       timeInForce='GoodTillCancel', clOrdID=order_uid, text=comment).result()[0]


def post_stop_order(ticker: str, qty: float, price: float, order_uid: str, comment: str = '') -> dict:
    return client_rest.Order.Order_new(symbol=ticker, orderQty=qty, ordType='Stop', stopPx=price, execInst='LastPrice',
                                       timeInForce='ImmediateOrCancel', clOrdID=order_uid, text=comment).result()[0]


def post_limit_order(ticker: str, qty: float, price: float, order_uid: str, comment: str = '') -> dict:
    return client_rest.Order.Order_new(symbol=ticker, orderQty=qty, ordType='Limit', price=price,
                                       clOrdID=order_uid, text=comment).result()[0]


def cancel_order(order_uid: str, comment: str) -> Optional[dict]:
    try:
        return client_rest.Order.Order_cancel(clOrdID=order_uid, text=comment).result()[0]
    except HTTPNotFound:
        return None


def cancel_all(comment: str) -> dict:
    return client_rest.Order.Order_cancelAll(text=comment).result()


client_rest = bitmex.bitmex(test=TEST_MODE, api_key=API_KEY, api_secret=API_SECRET)
