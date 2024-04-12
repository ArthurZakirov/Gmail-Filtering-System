import os
import argparse
import sys
import pandas as pd
import mailbox

COLUMNS = ["X-Gmail-Labels", "Message-ID", "Subject", "From", "To"]

parser = argparse.ArgumentParser()
parser.add_argument("--mbox_paths", nargs="+", default=["data/takeout-20240407T142025Z-001/Takeout/Gmail/Alle E-Mails einschließlich Spam-Nachrichten und E.mbox"])
parser.add_argument("--output_path", default="data/processed/email_data.csv")

args = parser.parse_args()

def get_email_body(message):
    def decode_part(part):
        try:
            return part.decode('utf-8')
        except UnicodeDecodeError:
            try:
                # Attempt to decode with a different encoding
                return part.decode('iso-8859-1')
            except UnicodeDecodeError:
                # If decoding fails, return a placeholder or an empty string
                return '[Unable to decode content]'

    if message.is_multipart():
        parts = [part.get_payload(decode=True) for part in message.walk() if part.get_content_type() == 'text/plain']
        return "".join(decode_part(part) for part in parts)
    else:
        payload = message.get_payload(decode=True)
        return decode_part(payload)


def main(args):
    dfs = []
    for mbox_path in args.mbox_paths:
        mbox = mailbox.mbox(mbox_path)

        emails = []
        for i, message in enumerate(mbox):
            email_data = {}
            for column in COLUMNS:
                email_data[column] = message[column]

            email_data["body"] = get_email_body(message)
            emails.append(email_data)

        df = pd.DataFrame(emails)
        dfs.append(df)

    dfs = pd.concat(dfs)
    os.makedirs(os.path.dirname(args.output_path), exist_ok=True)
    dfs.to_csv(args.output_path)

if __name__ == "__main__":
    main(args)

