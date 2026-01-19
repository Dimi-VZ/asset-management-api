import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from typing import Optional


def send_email(
    to_email: str,
    subject: str,
    body: str,
    smtp_host: Optional[str] = None,
    smtp_port: Optional[int] = None,
    smtp_user: Optional[str] = None,
    smtp_password: Optional[str] = None
) -> bool:
    if not smtp_host:
        smtp_host = settings.smtp_host
    if not smtp_port:
        smtp_port = settings.smtp_port
    if not smtp_user:
        smtp_user = settings.smtp_user
    if not smtp_password:
        smtp_password = settings.smtp_password
    
    if not smtp_user or not smtp_password:
        return False
    
    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if settings.smtp_use_tls:
                server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        return True
    except Exception:
        return False


def send_ip_change_alert(email: str, new_ip: str, old_ip: Optional[str] = None) -> bool:
    subject = "Security Alert: New Login Location Detected"
    
    if old_ip:
        body = f"""
Hello,

We detected a login to your account from a new location.

Previous IP Address: {old_ip}
New IP Address: {new_ip}

If this was you, no action is needed. If you did not log in from this location, please secure your account immediately.

Best regards,
Asset Management System
"""
    else:
        body = f"""
Hello,

This is your first login from this location.

IP Address: {new_ip}

If you did not log in, please secure your account immediately.

Best regards,
Asset Management System
"""
    
    return send_email(to_email=email, subject=subject, body=body)
