from fastapi import Request
from fastapi.responses import JSONResponse
from exceptions import AdvisorError

async def api_exception_handler(request: Request, exc: AdvisorError):
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc),
            "path": request.url.path,
        },
    )
