import uuid
from typing import Optional

import redis

client_redis = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
key_prefix = 'crypto_bot:next_gen:'


def _namespace_key(uid: str) -> str:
    return f'{key_prefix}order:{uid}'


def _init_order_key(uid: str) -> str:
    return f'{_namespace_key(uid)}:init'


def _profit_order_key(uid: str) -> str:
    return f'{_namespace_key(uid)}:profit'


def gen_uid() -> str:
    return uuid.uuid4().hex


def add_init_order(uid: str, stop_price: float, take_price: float, qty: float, color: str, ticker: str):
    return client_redis.hmset(_init_order_key(uid), {'stop': stop_price, 'take': take_price, 'qty': qty,
                                                     'color': color, 'ticker': ticker})


def add_profit_order(uid: str, pair_uid: str, parent_order_uid: str):
    return client_redis.hmset(_profit_order_key(uid), {'pair_uid': pair_uid, 'parent': parent_order_uid})


def get_init_order(uid: str) -> Optional[dict]:
    order = client_redis.hgetall(_init_order_key(uid))
    return None if not order else order


def get_profit_order(uid: str) -> Optional[str]:
    pair_order = client_redis.hgetall(_profit_order_key(uid))
    return None if not pair_order else pair_order['pair_uid']


def del_init_order(uid: str):
    return client_redis.delete(_init_order_key(uid))


def del_profit_order(uid: str):
    return client_redis.delete(_profit_order_key(uid))


