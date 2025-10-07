from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import routes
from starlette.middleware.base import BaseHTTPMiddleware
from middleware_services import middleware_log


origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://staging-proctor.test.com",
]

app = FastAPI()
# enable cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # allow all
    allow_headers=["*"],  # allow all
)
app.add_middleware(BaseHTTPMiddleware, dispatch=middleware_log)


app.include_router(routes.router)

