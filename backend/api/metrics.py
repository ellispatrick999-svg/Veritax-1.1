_metrics = {
    "requests": 0,
    "errors": 0,
}

def record_request():
    _metrics["requests"] += 1


def record_error():
    _metrics["errors"] += 1


def get_metrics():
    return _metrics.copy()
