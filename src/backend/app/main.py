# backend/app/main.py
from contextlib import asynccontextmanager

from app.api.v1 import health, kds, menu, order, payment, seat, webhook
from app.config import settings
from app.utils.timeout import start_timeout_worker, stop_timeout_worker
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    start_timeout_worker()
    yield
    # 关闭时
    stop_timeout_worker()


app = FastAPI(
    title="Clap Cafe Ordering API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 健康检查
app.include_router(health.router, tags=["Health"])

# API v1 路由
app.include_router(menu.router, prefix="/v1", tags=["Menu"])
app.include_router(order.router, prefix="/v1", tags=["Orders"])
app.include_router(payment.router, prefix="/v1", tags=["Payments"])
app.include_router(seat.router, prefix="/v1", tags=["Seats"])
app.include_router(webhook.router, prefix="/v1", tags=["Webhooks"])
app.include_router(kds.router, prefix="/v1", tags=["KDS"])
