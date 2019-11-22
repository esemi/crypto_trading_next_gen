from typing import Optional

import redis

client_rest = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
key_prefix = 'crypto_bot:next_gen:'


def _init_order_key(uid: str) -> str:
    return f'{key_prefix}init_order:{uid}'


def add_init_order(uid: str, stop_price: float, take_price: float):
    return client_rest.hmset(_init_order_key(uid), {
        'stop': stop_price,
        'take': take_price,
    })


def get_init_order(uid: str) -> Optional[dict]:
    order = client_rest.hgetall(_init_order_key(uid))
    return None if not order else order

