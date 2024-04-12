import pandas as pd
import numpy as np
import base64
import email
import urllib

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials



def get_label_mapping(service, user_id):
    response = service.users().labels().list(userId=user_id).execute()
    labels = response.get('labels', [])
    # Create a mapping from label IDs to label names
    return {label['id']: label['name'] for label in labels}

def get_mime_message(service, user_id, message_id):
    message = service.users().messages().get(userId=user_id, id=message_id, format='raw').execute()
    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
    mime_msg = email.message_from_bytes(msg_str)

    return mime_msg

def get_message_body(mime_msg):
    if mime_msg.is_multipart():
        for part in mime_msg.walk():
            # You may want to further check the content type here.
            if part.get_content_type() == 'text/plain':
                # Try to decode with utf-8, if failed, use 'latin1' or 'ignore' errors
                try:
                    return part.get_payload(decode=True).decode('utf-8')
                except UnicodeDecodeError:
                    return part.get_payload(decode=True).decode('latin1', errors='ignore')
    else:
        # Try to decode with utf-8, if failed, use 'latin1' or 'ignore' errors
        try:
            return mime_msg.get_payload(decode=True).decode('utf-8')
        except UnicodeDecodeError:
            return mime_msg.get_payload(decode=True).decode('latin1', errors='ignore')

def get_df_from_gmail_api(service, COLUMNS = ['From', 'To', 'Subject', 'Date']):
    label_mapping = get_label_mapping(service, 'me')

    messages = service.users().messages().list(userId="me").execute().get("messages")
    message_dicts = []

    for i in range(len(messages)):
        message_id = messages[i]["id"]
        message = service.users().messages().get(userId="me", id=message_id).execute()

        mime_msg = get_mime_message(service, 'me', message_id)
        message_body = get_message_body(mime_msg)

        message_label_ids = message.get("labelIds")
        message_headers = message.get("payload").get("headers")

        message_dict = {}
        message_dict["Labels"] = [label_mapping.get(label_id, "Unknown") for label_id in message_label_ids]
        message_dict["Body"] = message_body
        message_dict["ID"] = message.get("id")
        
        for header in message_headers:
            if header["name"] in COLUMNS:
                message_dict[header["name"]] = header["value"]

        message_dicts.append(message_dict)

    df = pd.DataFrame(message_dicts)
    return df