"""
Email Service — Strategy Pattern (抽象層 + 工廠函式)

用法：
    from app.services.email_service import get_email_service
    svc = get_email_service()
    await svc.send_verification_email(to_email, full_name, token)

透過 .env 的 EMAIL_PROVIDER 切換：
    EMAIL_PROVIDER=smtp       → SmtpEmailService
    EMAIL_PROVIDER=azure_acs  → AcsEmailService
    EMAIL_PROVIDER=none       → NullEmailService (開發用，只記 log)
"""

import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class EmailService(ABC):
    """所有 Email 服務的統一介面"""

    @abstractmethod
    async def send_verification_email(
        self,
        to_email: str,
        full_name: str,
        verification_url: str,
    ) -> bool:
        """寄出驗證信，成功回傳 True，失敗回傳 False"""
        ...

    @abstractmethod
    async def send_welcome_email(self, to_email: str, full_name: str) -> bool:
        """帳號驗證完成後的歡迎信（可選）"""
        ...


class NullEmailService(EmailService):
    """
    開發 / 測試用的空實作。
    EMAIL_PROVIDER=none 時啟用，只印 log，不實際寄信。
    """

    async def send_verification_email(
        self, to_email: str, full_name: str, verification_url: str
    ) -> bool:
        logger.warning(
            f"[NullEmailService] Verification email NOT sent (EMAIL_PROVIDER=none). "
            f"To: {to_email} | URL: {verification_url}"
        )
        return True  # 讓流程繼續

    async def send_welcome_email(self, to_email: str, full_name: str) -> bool:
        logger.warning(
            f"[NullEmailService] Welcome email NOT sent (EMAIL_PROVIDER=none). "
            f"To: {to_email}"
        )
        return True


# ── 工廠函式 ──────────────────────────────────────────────────────────────────

def get_email_service() -> EmailService:
    """
    根據 settings.EMAIL_PROVIDER 回傳對應的 EmailService 實作。
    在 FastAPI Dependency Injection 或直接呼叫都可以使用。
    """
    from app.core.config import settings, EmailProvider

    if settings.EMAIL_PROVIDER == EmailProvider.SMTP:
        from app.services.smtp_email import SmtpEmailService
        return SmtpEmailService()

    elif settings.EMAIL_PROVIDER == EmailProvider.AZURE_ACS:
        from app.services.acs_email import AcsEmailService
        return AcsEmailService()

    else:
        return NullEmailService()
