import base64
import os
import smtplib
import ssl
from collections.abc import Iterable
from email.message import EmailMessage
from functools import lru_cache

import pandas as pd
from dotenv import load_dotenv
from flask import Flask, request
from posit import connect

load_dotenv()
app = Flask(__name__)

SMTP_HOST = "smtp.office365.com"
SMTP_PORT = 587
CONNECT_OAUTH_INTEGRATION_GUID = os.environ.get("INTEGRATION_GUID")


@lru_cache(maxsize=1)
def get_connect_client():
    return connect.Client()


def get_access_token() -> str:
    if not CONNECT_OAUTH_INTEGRATION_GUID:
        raise RuntimeError("INTEGRATION_GUID is not configured.")

    credentials = get_connect_client().oauth.get_content_credentials(
        audience=CONNECT_OAUTH_INTEGRATION_GUID
    )
    access_token = credentials.get("access_token")
    if not access_token:
        raise RuntimeError("Posit Connect did not return an access token.")

    return access_token


def generate_xoauth2_string(username: str, access_token: str) -> str:
    auth_field = "auth=" + "Bearer " + access_token
    auth_string = f"user={username}\x01{auth_field}\x01\x01"
    return base64.b64encode(auth_string.encode()).decode()


def send_messages(
    messages: Iterable[EmailMessage],
    username: str,
    access_token: str,
) -> int:
    xoauth2 = generate_xoauth2_string(username, access_token)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.ehlo()
        smtp.starttls(context=ssl.create_default_context())
        smtp.ehlo()

        response_code, _ = smtp.docmd("AUTH", f"XOAUTH2 {xoauth2}")
        if response_code != 235:
            raise RuntimeError(
                f"SMTP OAuth authentication failed (SMTP code {response_code})."
            )

        count = 0
        for message in messages:
            smtp.send_message(message)
            count += 1

    return count


@app.route("/")
def hello_world():
    """
    Basic endpoint for API.

    Returns:
        str: Text "Hello, World!"
    """
    return "Hello, World!"


@app.post("/send_emails")
def send_emails():
    """
    Basic POST endpoint for API. Accepts JSON with keys "key", "email_subject",
    "email_text" and "data", where "data" is a DataFrame containing the names
    and email addresses of recipients. Columns in DataFrame must be "email_1", "email_2",
    "name_1" and "name_2".

    Returns:
        str: Number of emails sent
    """
    data = request.get_json()
    if data["key"] == os.environ.get("API_KEY"):
        df = pd.read_json(data["data"], orient="records")
        mailbox = os.environ.get("MAILBOX")
        if not mailbox:
            raise RuntimeError("MAILBOX is not configured.")

        def messages():
            for line in df.index:
                email_1 = df.loc[line, "email_1"]
                email_2 = df.loc[line, "email_2"]
                name_1 = df.loc[line, "name_1"]
                name_2 = df.loc[line, "name_2"]
                message = EmailMessage()
                message["Subject"] = data["email_subject"]
                message["To"] = f"{email_1}, {email_2}"
                message["From"] = mailbox
                message.set_content(
                    f"<p>Dear {name_1} and {name_2},</p>" + data["email_text"],
                    subtype="html",
                )
                yield message

        count = send_messages(
            messages(),
            username=mailbox,
            access_token=get_access_token(),
        )
        return f"{count} messages sent!"
    else:
        return "Invalid API key"


if __name__ == "__main__":
    app.run()
