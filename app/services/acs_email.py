"""
Azure Communication Services Email 實作

需要 .env 設定：
    EMAIL_PROVIDER=azure_acs
    ACS_CONNECTION_STRING=endpoint=https://xxx.communication.azure.com/;accesskey=xxx
    ACS_SENDER_ADDRESS=DoNotReply@xxx.azurecomm.net  # 或自訂網域

Azure Portal 設定步驟：
    1. 搜尋 "Communication Services" → 新建資源
    2. 左側選 "Email" → "Add domain"
    3. 選擇 "Azure managed domain" (快速) 或 Custom domain (公司網域)
    4. 左側選 "Keys" → 複製 Connection String → 貼到 .env

注意：需安裝 SDK
    pip install azure-communication-email
"""

import logging
from app.services.email_service import EmailService
from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_verification_html(full_name: str, verification_url: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>驗證您的帳號</title>
</head>
<body style="margin:0;padding:0;background:#0f0f0f;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f0f0f;padding:40px 0;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="background:#1a1a1a;border-radius:16px;overflow:hidden;border:1px solid #2a2a2a;">
        <!-- Header -->
        <tr>
          <td style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);padding:40px 40px 30px;text-align:center;">
            <div style="font-size:28px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">
              Ɐ <span style="color:#4ade80;">Platform</span>
            </div>
            <div style="font-size:13px;color:#94a3b8;margin-top:6px;letter-spacing:1px;">AI ENTERPRISE SUITE</div>
          </td>
        </tr>
        <!-- Body -->
        <tr>
          <td style="padding:40px;">
            <h2 style="color:#f1f5f9;font-size:22px;margin:0 0 16px;font-weight:700;">嗨，{full_name} 👋</h2>
            <p style="color:#94a3b8;font-size:15px;line-height:1.7;margin:0 0 24px;">
              感謝您註冊 AI Platform！<br>
              請點擊下方按鈕驗證您的電子郵件地址，以完成帳號建立。
            </p>
            <div style="text-align:center;margin:32px 0;">
              <a href="{verification_url}"
                 style="display:inline-block;background:linear-gradient(135deg,#4ade80,#22c55e);
                        color:#000000;font-weight:700;font-size:15px;
                        padding:14px 40px;border-radius:50px;text-decoration:none;">
                ✉️ &nbsp;立即驗證帳號
              </a>
            </div>
            <div style="background:#0f0f0f;border-radius:8px;padding:16px;margin:24px 0;">
              <p style="color:#64748b;font-size:12px;margin:0 0 6px;">如果按鈕無效，請複製以下連結到瀏覽器：</p>
              <p style="color:#4ade80;font-size:12px;word-break:break-all;margin:0;">{verification_url}</p>
            </div>
            <p style="color:#64748b;font-size:13px;margin:0;">
              ⏰ 此連結將在 <strong style="color:#fbbf24;">24 小時</strong>後失效。<br>
              如果您沒有申請此帳號，請忽略此郵件。
            </p>
          </td>
        </tr>
        <tr>
          <td style="padding:20px 40px;border-top:1px solid #2a2a2a;text-align:center;">
            <p style="color:#475569;font-size:12px;margin:0;">
              © 2025 AI Platform. All rights reserved.<br>
              此郵件由系統自動發送，請勿直接回覆。
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def _build_welcome_html(full_name: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head><meta charset="UTF-8"><title>歡迎加入 AI Platform</title></head>
<body style="margin:0;padding:0;background:#0f0f0f;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f0f0f;padding:40px 0;">
    <tr><td align="center">
      <table width="560" cellpadding="0" cellspacing="0" style="background:#1a1a1a;border-radius:16px;overflow:hidden;border:1px solid #2a2a2a;">
        <tr>
          <td style="background:linear-gradient(135deg,#1a1a2e,#16213e,#0f3460);padding:40px;text-align:center;">
            <div style="font-size:48px;margin-bottom:12px;">🎉</div>
            <div style="font-size:24px;font-weight:800;color:#fff;">歡迎加入，{full_name}！</div>
            <div style="color:#94a3b8;margin-top:8px;">您的帳號已成功驗證</div>
          </td>
        </tr>
        <tr>
          <td style="padding:40px;">
            <p style="color:#94a3b8;font-size:15px;line-height:1.7;margin:0;">
              您現在可以登入並開始使用 AI Platform 的所有功能。
            </p>
          </td>
        </tr>
        <tr>
          <td style="padding:20px 40px;border-top:1px solid #2a2a2a;text-align:center;">
            <p style="color:#475569;font-size:12px;margin:0;">© 2025 AI Platform. All rights reserved.</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


class AcsEmailService(EmailService):
    """Azure Communication Services Email 實作"""

    def _get_client(self):
        """懶載入 ACS client，只在實際使用時才 import SDK"""
        try:
            from azure.communication.email import EmailClient
        except ImportError:
            raise RuntimeError(
                "azure-communication-email SDK 未安裝。\n"
                "請執行: pip install azure-communication-email"
            )

        if not settings.ACS_CONNECTION_STRING:
            raise ValueError(
                "ACS_CONNECTION_STRING 未設定。\n"
                "請在 .env 加入: ACS_CONNECTION_STRING=<your-connection-string>"
            )

        return EmailClient.from_connection_string(settings.ACS_CONNECTION_STRING)

    def _send(self, to_email: str, subject: str, html_body: str) -> bool:
        try:
            client = self._get_client()

            sender = settings.ACS_SENDER_ADDRESS
            if not sender:
                raise ValueError("ACS_SENDER_ADDRESS 未設定於 .env")

            message = {
                "senderAddress": sender,
                "recipients": {
                    "to": [{"address": to_email}]
                },
                "content": {
                    "subject": subject,
                    "html": html_body,
                },
            }

            # ACS 是同步 SDK，用 poller 等待結果
            poller = client.begin_send(message)
            result = poller.result()

            logger.info(
                f"[AcsEmailService] Email sent to {to_email}: {subject} "
                f"| MessageId: {result.get('id', 'N/A')}"
            )
            return True

        except Exception as e:
            logger.error(f"[AcsEmailService] Failed to send email to {to_email}: {e}")
            return False

    async def send_verification_email(
        self, to_email: str, full_name: str, verification_url: str
    ) -> bool:
        html = _build_verification_html(full_name, verification_url)
        return self._send(
            to_email=to_email,
            subject="【AI Platform】驗證您的電子郵件地址",
            html_body=html,
        )

    async def send_welcome_email(self, to_email: str, full_name: str) -> bool:
        html = _build_welcome_html(full_name)
        return self._send(
            to_email=to_email,
            subject="【AI Platform】歡迎加入！您的帳號已驗證",
            html_body=html,
        )
