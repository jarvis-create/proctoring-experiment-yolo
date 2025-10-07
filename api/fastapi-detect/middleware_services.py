from fastapi import Request
from loggers import routelogger

import time


async def middleware_log(request: Request, call_next):
    start = time.time()

    response = await call_next(request)

    process_time = time.time() - start

    log_dict = {
        "url": request.url.path,
        "method": request.method,
        "process_time": process_time,
    }

    routelogger.info(log_dict, extra=log_dict)
    return response