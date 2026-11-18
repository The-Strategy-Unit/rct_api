# RCT Emailer API

Basic Flask API for sending emails to pairs of users.

Companion repository: [rct_streamlit](https://github.com/The-Strategy-Unit/rct_streamlit/) which provides a frontend for users to
upload their files and interact with the API.

Configure these environment variables for the API:

- `API_KEY`
- `MAILBOX`
- `INTEGRATION_GUID`

`MAILBOX` is the Microsoft 365 mailbox used as both the SMTP OAuth
username and the message sender. `INTEGRATION_GUID` is the
audience/GUID of the OAuth integration configured in Posit Connect. The API
must run as content in Posit Connect so the Posit SDK can obtain credentials
for that integration. Configure the integration and its Microsoft 365 SMTP
permissions in Connect and Exchange Online; no mailbox password is used.
