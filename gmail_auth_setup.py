import argparse
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

parser = argparse.ArgumentParser()
parser.add_argument("--token_path", default="config/token.json")
parser.add_argument("--credentials_path", default="config/credentials.json")
parser.add_argument(
    "--scopes", nargs="+", default=["https://www.googleapis.com/auth/gmail.readonly"]
)


def parse_arguments():
    """Parse command line arguments."""
    return parser.parse_args()


def authorize_gmail_access(args):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    token_path = args.token_path
    credentials_path = args.credentials_path
    SCOPES = args.scopes

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"

            auth_url, _ = flow.authorization_url(prompt="consent")

            print("Go to this URL to authorize the app:", auth_url)
            code = input("Enter the authorization code: ")
            flow.fetch_token(code=code)

            creds = flow.credentials
        with open(token_path, "w") as token:
            token.write(creds.to_json())


args = None

if __name__ == "__main__":
    args = parse_arguments()
    authorize_gmail_access(args)
