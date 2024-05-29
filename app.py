from flask import Flask, request
from flask_mail import Mail, Message
import pandas as pd
from dotenv import load_dotenv
import os
import json

load_dotenv()
app = Flask(__name__)

app.config["MAIL_SERVER"] = "smtp.office365.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False

mail = Mail(app)


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
    Basic POST endpoint for API. Accepts JSON of a DataFrame containing the names
    and email addresses of recipients. Columns must be "email_1", "email_2",
    "name_1" and "name_2". Must include valid API key as "key" in query string.

    Returns:
        str: Number of emails sent
    """
    data = request.get_json()
    if data['key'] == os.environ.get("API_KEY"):
        df = pd.read_json(data['data'], orient="records")
        with mail.connect() as conn:
            count = 0
            for line in df.index:
                print(line)
                count += 1
                email_1 = df.loc[line, "email_1"]
                email_2 = df.loc[line, "email_2"]
                name_1 = df.loc[line, "name_1"]
                name_2 = df.loc[line, "name_2"]
                msg = Message(
                    subject="Your Randomized Coffee Trial pairing",
                    recipients=[email_1, email_2], 
                    sender=os.environ.get("MAIL_USERNAME"),
                )
                msg.body = f"""
                            Dear {name_1} and {name_2}, you are Randomized Coffee 
                            Trial buddies for this month! Please arrange a 30 minute 
                            conversation at a mutually convenient time. We hope you 
                            enjoy it!
                            """
                conn.send(msg)
            return f"{count} messages sent!"
    else:
        return "Invalid API key"

if __name__ == "__main__":
    app.run()
