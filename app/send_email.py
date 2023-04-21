import smtplib
from email.utils import formataddr
from email.message import EmailMessage
from email.utils import formataddr
from email.mime.text import MIMEText

from config import Config


def invite_body(url):
    return f"""Helo,
Here is your <a href='{url}'>link to the book</a>
"""


def send_email(to, subject, body):
    msg = EmailMessage()
    msg['From'] = formataddr((Config.EMAIL_FROM_NAME, Config.EMAIL_FROM))
    msg['To'] = to
    msg['Subject'] = subject
    msg.set_content(MIMEText(body, 'html'))

    with smtplib.SMTP(Config.SMTP_HOST) as s:
        s.send_message(msg)
