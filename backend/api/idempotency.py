_idempotency_store = {}

def check_idempotency(key: str):
    if key in _idempotency_store:
        return _idempotency_store[key]


def store_idempotency(key: str, response):
    _idempotency_store[key] = response
