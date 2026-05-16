# backend/app/core/email_service.py
"""Email sending via Resend."""
import secrets
from datetime import datetime, timedelta, timezone

import httpx
from app.config import settings


async def send_password_reset_email(to_email: str, reset_link: str) -> bool:
    """Send a password reset email via Resend."""
    if not settings.RESEND_API_KEY:
        # Fallback: log the link if Resend is not configured
        print(f"[Email] Password reset link (no Resend configured): {reset_link}")
        return True

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": settings.RESEND_FROM_EMAIL,
                    "to": [to_email],
                    "subject": "Reset your Clap Cafe admin password",
                    "html": f"""
                    <div style="font-family: sans-serif; max-width: 480px; margin: 0 auto;">
                      <h2 style="color: #6c5ce7;">Clap Cafe Admin</h2>
                      <p>You requested a password reset. Click the button below to reset your password:</p>
                      <a href="{reset_link}" style="display: inline-block; background: #6c5ce7; color: #fff; padding: 12px 24px; border-radius: 6px; text-decoration: none; margin: 16px 0;">Reset Password</a>
                      <p style="color: #666; font-size: 14px;">If you didn't request this, please ignore this email. This link expires in 1 hour.</p>
                    </div>
                    """,
                    "text": f"Reset your password: {reset_link}\n\nIf you didn't request this, ignore this email. Link expires in 1 hour.",
                },
                timeout=10.0,
            )
            response.raise_for_status()
            print(
                f"[Email] Sent password reset to {to_email}, response: {response.status_code}"
            )
            return True
        except Exception as e:
            print(f"[Email] Failed to send email: {e}")
            return False


def generate_reset_token() -> str:
    """Generate a secure random reset token."""
    return secrets.token_urlsafe(32)


def get_reset_link(token: str, base_url: str) -> str:
    """Build the password reset link with the token."""
    return f"{base_url}/reset-password?token={token}"
