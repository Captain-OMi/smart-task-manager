# This file is used to send registration OTP emails for the Smart Task Manager project by reading SMTP settings from environment variables and delivering verification codes before a new account is created.

import os
import smtplib
from email.message import EmailMessage


def send_registration_otp(email, name, otp):
    mail_server = os.getenv("MAIL_SERVER")
    mail_port = int(os.getenv("MAIL_PORT", "587"))
    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")
    mail_sender = os.getenv("MAIL_DEFAULT_SENDER") or mail_username
    use_tls = os.getenv("MAIL_USE_TLS", "true").lower() == "true"

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

    with smtplib.SMTP(mail_server, mail_port) as smtp:
        if use_tls:
            smtp.starttls()
        smtp.login(mail_username, mail_password)
        smtp.send_message(message)
