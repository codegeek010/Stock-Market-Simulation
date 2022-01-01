import sentry_sdk
from fastapi import Depends, FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware


from common.authentication import get_current_user
from config.config import settings
from common.metadata import tags_metadata
from routes.stocks import stocks_router
from routes.transactions import transactions_router
from routes.user import user_router

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=0.5,
)

app = FastAPI(
    title="Stock Market Simulation",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs/swagger",
    redoc_url="/docs/redoc",
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping", tags=["Health"])
async def health() -> ORJSONResponse:
    """
    Health Check
    """
    return ORJSONResponse(status_code=200, content={"message": "pong"})


PROTECTED = [Depends(get_current_user)]

app.include_router(user_router, prefix="/api/v1", tags=["User"])
app.include_router(
    stocks_router, prefix="/api/v1", tags=["Stocks"], dependencies=PROTECTED
)
app.include_router(
    transactions_router, prefix="/api/v1", tags=["Transactions"], dependencies=PROTECTED
)
