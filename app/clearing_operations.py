import logging
from datetime import datetime
from typing import List

from bitmex_rest import cancel_order, get_self_orders
from storage import del_init_order, get_init_order


def fetch_orders_for_clearing() -> List[str]:
    filtered_orders = []
    self_orders = get_self_orders()
    for order in self_orders:
        uid = order['clOrdID']
        logging.info(f'fetch_orders_for_clearing test order {order}')
        init_order = get_init_order(uid)
        if not init_order:
            logging.info('skip by not found init order into storage')
            continue

        if order['ordStatus'] != 'New':
            logging.info(f'skip by order status {order["ordStatus"]}')
            continue

        if order['leavesQty'] != order['orderQty']:
            logging.info(f'skip partial filled order {order["leavesQty"]}/{order["orderQty"]}')
            continue

        time_diff_offset = init_order['clearing_offset']

        time_delta = datetime.utcnow() - order['timestamp'].replace(tzinfo=None)
        logging.info(f'order time={order["timestamp"]}; delta from now UTC={time_delta}; {time_diff_offset=}')
        if time_delta.total_seconds() < time_diff_offset:
            logging.info(f'skip by time diff {order["timestamp"]}')
            continue

        filtered_orders.append(uid)
    return filtered_orders


def clear_order(order_uid: str) -> bool:
    cancel_resp = cancel_order(order_uid, 'cancelled by clearing')
    logging.info(f'cancel order resp={cancel_resp}')
    if cancel_resp:
        del_init_order(order_uid)
        return True
    return False
