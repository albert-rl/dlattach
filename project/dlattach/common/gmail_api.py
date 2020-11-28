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


class GmailSvc:
    """ Class for Gmail service """

    def __init__(self, user):
        """ Connect to google via gmail-api building a service """
        self.svc = None
        self.cred = None
        self.msg_list = None
        self.curr_msg = None
        self.curr_mime = None

        self.user = user

        # Get paths
        credentials_dir = path().absolute().resolve().parent.joinpath('resources', 'credentials')
        token_path = credentials_dir.joinpath('token.pickle')
        credentials_path = credentials_dir.joinpath('gmail-python-dlattach.json')

        # TODO: Use a Google Service Account for OAuth
        # TODO: https://levelup.gitconnected.com/how-to-set-up-credentials-to-and-send-an-email-using-the-gmail-api-259145a0a5ec
        # TODO: https://cran.r-project.org/web/packages/gargle/vignettes/get-api-credentials.html

        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if token_path.exists():
            with open(token_path, 'rb') as token:
                self.cred = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not self.cred or not self.cred.valid:
            if self.cred and self.cred.expired and self.cred.refresh_token:
                self.cred.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                self.cred = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(token_path, 'wb') as token:
                pickle.dump(self.cred, token)

        self.svc = build('gmail', 'v1', credentials=self.cred)

    def get_messages(self):
        """ Get all messages in the form of a dict """
        # TODO: add params to select specific inboxes
        try:
            messages = []
            msgs = self.svc.users().messages()

            # Manage pagination
            resp = msgs.list(userId=self.user, includeSpamTrash=False)
            while resp is not None:
                msg_pag = resp.execute()
                messages.extend(msg_pag['messages'])
                resp = msgs.list_next(resp, msg_pag)

            self.msg_list = messages

        except Exception as error:
            print('An error occurred: %s' % error)

    def get_message(self, msg_id):
        """ Get content of a message based on its ID """
        try:
            self.curr_msg = self.svc.users().messages().get(userId=self.user, id=msg_id, format='metadata').execute()

        except Exception as error:
            print('An error occurred: %s' % error)

    def get_mime_message(self, msg_id):
        """ Get message in mime format """
        try:
            message = self.svc.users().messages().get(userId=self.user, id=msg_id, format='raw').execute()
            # print('Message snippet: %s' % message['snippet'])
            msg_str = base64.urlsafe_b64decode(message['raw'].encode("utf-8")).decode("utf-8")

            self.curr_mime = email.message_from_string(msg_str)

        except Exception as error:
            print('An error occurred: %s' % error)

    def dl_attach(self, store_dir):
        """ Download attachments to specified folders """
        try:
            # Get all messages except in trash and spam
            self.get_messages()

            for msg in self.msg_list:
                message = self.svc.users().messages().get(userId=self.user, id=msg['id']).execute()

                # Check if message has attachments
                if 'parts' in message['payload']:
                    for part in message['payload']['parts']:
                        if 'filename' in part and 'body' in part and 'attachmentId' in part['body']:
                            # Get attachment
                            attachment = self.svc.users().messages().attachments().get(id=part['body']['attachmentId'], userId=self.user, messageId=msg['id']).execute()
                            file_data = base64.urlsafe_b64decode(attachment['data'].encode('utf-8'))

                            # Do not override attachments with the same name
                            i = 0
                            filename = path(part['filename'])
                            file_path = path(store_dir).joinpath(f'{filename.stem}_{i}{filename.suffix}')

                            while file_path.exists():
                                i += 1
                                file_path = path(store_dir).joinpath(f'{filename.stem}_{i}{filename.suffix}')

                            fp = open(file_path, 'wb')
                            fp.write(file_data)
                            fp.close()

        except Exception as error:
            print('1 An error occurred: %s' % error)

    def close(self):
        """ Close service """
        if self.svc is not None:
            self.svc.close()
            self.svc = None


# Debug purposes
if __name__ == '__main__':
    service = GmailSvc(user='me')
    service.get_messages()

    print(service.msg_list)

    service.close()





    # service = build_service()
    # result_msg = get_messages(service=service, user_id='me')
    #
    # # print(len(result_msg))
    # for msg in result_msg:
    #     get_attachments(service=service, user_id='me', msg_id=msg['id'], store_dir='.')
    #
    # service.close()
