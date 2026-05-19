# This file is used to send registration OTP emails for the Smart Task Manager project by reading SMTP settings from environment variables and delivering verification codes before a new account is created.

import os
import smtplib
import json
from email.message import EmailMessage
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def send_registration_otp(email, name, otp):
    resend_api_key = os.getenv("RESEND_API_KEY")
    if resend_api_key:
        send_registration_otp_with_resend(email, name, otp, resend_api_key)
        return

    mail_server = os.getenv("MAIL_SERVER")
    mail_port = int(os.getenv("MAIL_PORT", "587"))
    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")
    mail_sender = os.getenv("MAIL_DEFAULT_SENDER") or mail_username
    use_tls = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    mail_timeout = int(os.getenv("MAIL_TIMEOUT", "8"))

    if not all([mail_server, mail_username, mail_password, mail_sender]):
        raise RuntimeError("Email SMTP settings are missing. Please configure MAIL_* variables.")

    message = EmailMessage()
    message["Subject"] = "Smart Task Manager verification code"
    message["From"] = mail_sender
    message["To"] = email
    message.set_content(
        f"Hello {name},\n\n"
        f"Your Smart Task Manager verification code is: {otp}\n\n"
        "This code is valid for 10 minutes.\n\n"
        "If you did not request this account, please ignore this email."
    )

    try:
        with smtplib.SMTP(mail_server, mail_port, timeout=mail_timeout) as smtp:
            if use_tls:
                smtp.starttls()
            smtp.login(mail_username, mail_password)
            smtp.send_message(message)
    except (OSError, TimeoutError, smtplib.SMTPException) as error:
        raise RuntimeError(f"Unable to send verification email: {error}") from error


def send_registration_otp_with_resend(email, name, otp, api_key):
    sender = os.getenv("RESEND_FROM_EMAIL", "Smart Task Manager <onboarding@resend.dev>")
    timeout = int(os.getenv("RESEND_TIMEOUT", "10"))
    payload = {
        "from": sender,
        "to": [email],
        "subject": "Smart Task Manager verification code",
        "text": (
            f"Hello {name},\n\n"
            f"Your Smart Task Manager verification code is: {otp}\n\n"
            "This code is valid for 10 minutes.\n\n"
            "If you did not request this account, please ignore this email."
        ),
    }

    request = Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            if response.status >= 400:
                raise RuntimeError(f"Resend email API failed with status {response.status}.")
    except HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Resend email API failed: {details}") from error
    except URLError as error:
        raise RuntimeError(f"Unable to reach Resend email API: {error.reason}") from error
