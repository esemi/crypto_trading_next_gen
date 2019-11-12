import warnings

from configs import TEST_MODE, API_KEY, API_SECRET

warnings.filterwarnings("ignore")
client = None


def init_client(test_mode: bool):
    import bitmex
    global client
    client = bitmex.bitmex(test=test_mode, api_key=API_KEY, api_secret=API_SECRET)


def get_buckets(ticker: str, count: int) -> list:
    return client.Trade.Trade_getBucketed(binSize='1h', partial=False, symbol=ticker, count=count,
                                          reverse=True).result()[0]


def post_order(ticker: str, qty: float, price: float, order_uid: str) -> dict:
    resp = client.Order.Order_new(symbol=ticker, orderQty=qty, ordType='Stop', stopPx=price, clOrdID=order_uid, text='Init order by supervisor.py').result()
    print(resp)
    print(dir(resp))
    return resp[0]


init_client(TEST_MODE)
