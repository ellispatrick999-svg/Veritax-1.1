import time
from fastapi import HTTPException, Request

RATE_LIMIT = 100  # requests
WINDOW_SECONDS = 60

_clients = {}

def rate_limiter(request: Request):
    ip = request.client.host
    now = time.time()

    window = _clients.get(ip, [])
    window = [t for t in window if now - t < WINDOW_SECONDS]

    if len(window) >= RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    window.append(now)
    _clients[ip] = window
