"""
Structured Logging Configuration
統一的日誌設定：開發環境用彩色輸出，生產環境可切換為 JSON 格式。
未來可無痛接入 Azure Application Insights。
"""
import logging
import sys
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


def setup_logging(level: str = "INFO"):
    """
    初始化全域 logging 設定。
    呼叫一次即可，通常在 main.py 最上面。
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 避免重複加入 handler
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    # 降低第三方套件的 log 等級，減少噪音
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    自動記錄每個 HTTP request 的 method, path, status_code 和 latency。
    
    範例輸出：
    2026-03-25 18:30:00 | INFO    | app.core.logging_config | POST /api/v1/chat/send -> 200 (234ms)
    """

    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger(__name__)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        response = await call_next(request)
        
        duration_ms = round((time.time() - start_time) * 1000)
        
        # 只記錄 API 路由，略過靜態檔案與 health check
        path = request.url.path
        if path.startswith("/api/") or path == "/health":
            log_method = self.logger.info if response.status_code < 400 else self.logger.warning
            if response.status_code >= 500:
                log_method = self.logger.error
            
            log_method(
                "%s %s -> %d (%dms)",
                request.method,
                path,
                response.status_code,
                duration_ms,
            )

        return response
