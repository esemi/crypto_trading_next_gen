from typing import Optional

import redis

client_rest = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
key_prefix = 'crypto_bot:next_gen:'


def _init_order_key(uid: str) -> str:
    return f'{key_prefix}init_order:{uid}'


def _profit_order_key(uid: str) -> str:
    return f'{key_prefix}profit_order:{uid}'


def add_init_order(uid: str, stop_price: float, take_price: float):
    return client_rest.hmset(_init_order_key(uid), {'stop': stop_price, 'take': take_price})


def add_profit_order(uid: str, pair_uid: str):
    return client_rest.set(_profit_order_key(uid), pair_uid)


def get_init_order(uid: str) -> Optional[dict]:
    order = client_rest.hgetall(_init_order_key(uid))
    return None if not order else order


def get_profit_order(uid: str) -> Optional[dict]:
    pair_order_uid = client_rest.get(_profit_order_key(uid))
    return None if not pair_order_uid else pair_order_uid

