import bitmex

from configs import TEST_MODE, API_KEY, API_SECRET


def get_buckets(ticker: str, count: int) -> list:
    return client_rest.Trade.Trade_getBucketed(binSize='1h', partial=False, symbol=ticker, count=count,
                                               reverse=True).result()[0]


def post_stop_order(ticker: str, qty: float, trigger_price: float, order_price: float, order_uid: str, comment: str = '') -> dict:
    return client_rest.Order.Order_new(symbol=ticker, orderQty=qty, ordType='StopLimit', stopPx=trigger_price,
                                       execInst='LastPrice', price=order_price,
                                       timeInForce='ImmediateOrCancel', clOrdID=order_uid, text=comment).result()[0]


def post_limit_order(ticker: str, qty: float, price: float, order_uid: str, comment: str = '') -> dict:
    return client_rest.Order.Order_new(symbol=ticker, orderQty=qty, ordType='Limit', price=price,
                                       clOrdID=order_uid, text=comment).result()[0]


def cancel_order(order_uid: str, comment: str) -> dict:
    return client_rest.Order.Order_cancel(clOrdID=order_uid, text=comment).result()[0]


def cancel_all(comment: str) -> dict:
    return client_rest.Order.Order_cancelAll(text=comment).result()


client_rest = bitmex.bitmex(test=TEST_MODE, api_key=API_KEY, api_secret=API_SECRET)
