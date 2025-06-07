import pandas as pd
import base64
import email
from tqdm import tqdm

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def fetch_label_mapping(service, user_id):
    response = service.users().labels().list(userId=user_id).execute()
    labels = response.get('labels', [])
    return {label['id']: label['name'] for label in labels}

def fetch_mime_message(service, user_id, message_id):
    message = service.users().messages().get(userId=user_id, id=message_id, format='raw').execute()
    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
    mime_msg = email.message_from_bytes(msg_str)
    return mime_msg

def fetch_email_body(mime_msg):
    if mime_msg.is_multipart():
        for part in mime_msg.walk():
            if part.get_content_type() == 'text/plain':
                try:
                    return part.get_payload(decode=True).decode('utf-8')
                except UnicodeDecodeError:
                    return part.get_payload(decode=True).decode('latin1', errors='ignore')
    else:
        try:
            return mime_msg.get_payload(decode=True).decode('utf-8')
        except UnicodeDecodeError:
            return mime_msg.get_payload(decode=True).decode('latin1', errors='ignore')

def fetch_gmail_messages_as_df(
    service,
    columns=['From', 'To', 'Subject', 'Date'],
    q=None  
):
    label_mapping = fetch_label_mapping(service, 'me')
    message_dicts = []
    page_token = None

    total = service.users().messages().list(userId="me", q=q, maxResults=1).execute().get('resultSizeEstimate', 0)
    pbar = tqdm(total=total)


    while True:
        params = {'userId': "me"}
        if page_token:
            params['pageToken'] = page_token
        if q:
            params['q'] = q

        response = service.users().messages().list(**params).execute()
        messages = response.get("messages", [])

        for msg in messages:
            message_id = msg["id"]
            message = service.users().messages().get(userId="me", id=message_id).execute()

            mime_msg = fetch_mime_message(service, 'me', message_id)
            message_body = fetch_email_body(mime_msg)

            message_label_ids = message.get("labelIds", [])
            message_headers = message.get("payload", {}).get("headers", [])

            message_dict = {}
            message_dict["Labels"] = [label_mapping.get(label_id, "Unknown") for label_id in message_label_ids]
            message_dict["Body"] = message_body
            message_dict["ID"] = message.get("id")

            for header in message_headers:
                if header["name"] in columns:
                    message_dict[header["name"]] = header["value"]

            message_dicts.append(message_dict)

            pbar.update(1)
        page_token = response.get('nextPageToken')
        if not page_token:
            break
        
    pbar.close()
    df = pd.DataFrame(message_dicts)
    return df
