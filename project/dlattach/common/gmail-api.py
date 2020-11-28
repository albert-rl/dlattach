# TODO: USE GMAIL API: https://developers.google.com/gmail/api/quickstart/python
# TODO: USE GMAIL API: https://blog.mailtrap.io/send-emails-with-gmail-api/
# TODO: USE GMAIL API: https://medium.com/better-programming/a-beginners-guide-to-the-google-gmail-api-and-its-documentation-c73495deff08
# TODO: USE GMAIL API: https://gist.github.com/Julian-Nash/428503b040047f49a40825f83ce152b0

from __future__ import print_function  # TODO: Remove once print is not used in the code
import pickle
import base64
import email
import logging
from pathlib import Path as path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def build_service():
    """
    Connect to google via google-api building a service
    :return: build service
    """
    cred = None

    # Get paths
    credentials_dir = path().absolute().resolve().parent.joinpath('resources', 'credentials')
    token_path = credentials_dir.joinpath('token.pickle')
    credentials_path = credentials_dir.joinpath('gmail-python-attach.json')

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if token_path.exists():
        with open(token_path, 'rb') as token:
            cred = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            cred = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(cred, token)

    return build('gmail', 'v1', credentials=cred)


def get_messages(service, user_id):
    """

    :param service:
    :param user_id:
    :return:
    """

    # TODO: get a look at pagination: https://github.com/googleapis/google-api-python-client/blob/master/docs/pagination.md

    try:
        messages = []
        # resp = service.users().messages().list(userId=user_id, maxResults=500, includeSpamTrash=False).execute()
        # if 'messages' in resp:
        #     messages.extend(resp['messages'])
        #
        # while 'nextPageToken' in resp:
        #     page = resp['nextPageToken']
        #     resp = service.users().messages().list(userId=user_id, pageToken=page, maxResults=500, includeSpamTrash=False).execute()
        #     messages.extend(resp['messages'])

        msgs = service.users().messages()
        resp = msgs.list(user_id=user_id, includeSpamTrash=False)
        while resp is not None:
            msg_pag = resp.execute()
            messages.extend(msg_pag['messages'])
            resp = msgs.list_next(resp, msg_pag)

        return messages

    except Exception as error:
        print('An error occurred: %s' % error)


def get_message(service, user_id, msg_id):
    """

    :param service:
    :param user_id:
    :param msg_id:
    :return:
    """
    try:
        return service.users().messages().get(userId=user_id, id=msg_id, format='metadata').execute()

    except Exception as error:
        print('An error occurred: %s' % error)


def get_mime_message(service, user_id, msg_id):
    """

    :param service:
    :param user_id:
    :param msg_id:
    :return:
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        print('Message snippet: %s' % message['snippet'])
        msg_str = base64.urlsafe_b64decode(message['raw'].encode("utf-8")).decode("utf-8")
        mime_msg = email.message_from_string(msg_str)

        return mime_msg

    except Exception as error:
        print('An error occurred: %s' % error)


def get_attachments(service, user_id, msg_id, store_dir):
    """

    :param service:
    :param user_id:
    :param msg_id:
    :param store_dir:
    :return:
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()

        # TODO: Better way to do this -> https://stackoverflow.com/questions/43491287/elegant-way-to-check-if-a-nested-key-exists-in-a-dict
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                # TODO: Better way to do this -> https://stackoverflow.com/questions/43491287/elegant-way-to-check-if-a-nested-key-exists-in-a-dict
                if 'filename' in part and 'body' in part and 'attachmentId' in part['body']:
                    attachment = service.users().messages().attachments().get(id=part['body']['attachmentId'], userId=user_id, messageId=msg_id).execute()

                    file_data = base64.urlsafe_b64decode(attachment['data'].encode('utf-8'))
                    # file_path = path(store_dir).joinpath(part['filename'])

                    # f = open(file_path, 'wb')
                    # f.write(file_data)
                    # f.close()

                    try:
                        i = 0
                        filename = path(part['filename'])
                        file_path = path(store_dir).joinpath(f'{filename.stem}_{i}{filename.suffix}')

                        # Get file name and path
                        while file_path.exists():
                            i += 1
                            file_path = path(store_dir).joinpath(f'{filename.stem}_{i}{filename.suffix}')

                        fp = open(file_path, 'wb')
                        fp.write(file_data)
                        fp.close()

                        # logging.debug(f'{filename.stem}_{i}{filename.suffix}' + ' imported.')

                    # TODO: Remove try
                    except Exception as error:
                        print('2 An error occurred: %s' % error)
                        # logging.warning('Could not import attachment: ' + file_name.replace('\n', ' ').replace('\r', ''))

    except Exception as error:
        print('1 An error occurred: %s' % error)


# Debug purposes
if __name__ == '__main__':
    service = build_service()
    result_msg = get_messages(service=service, user_id='me')

    # print(len(result_msg))
    for msg in result_msg:
        # mime = get_mime_message(service=service, user_id='me', msg_id=msg['id'])
        get_attachments(service=service, user_id='me', msg_id=msg['id'], store_dir='.')

    service.close()
