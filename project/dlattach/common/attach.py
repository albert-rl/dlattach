# Make sure you have IMAP enabled in your gmail settings.
# Enable access to less secure applications to gmail
# Disable access after !!
# inspired from code of: http://tech.franzone.blog/2012/11/29/counting-messages-in-imap-folders-in-python/

# TODO: USE GMAIL API ?

import os
import sys
import logging
import traceback
import imaplib
import email


def get_folder(imap, flag):
    """
    Get the Gmail folder name based on its flag
    :param imap: IMAP Client
    :param flag: Flag to search for
    :return: Folder name
    """
    resp, folder_list = imap.list()
    for folder_item in folder_list:
        flags, name = folder_item.decode().split(' "/" ')

        for flag_item in flags.split('\\'):
            if flag_item.strip().strip('(').strip(')') == flag:
                return name


def download_attachments(user, password, dest_dir):
    """
    Download all attachments from Mail with IMAP
    :param user: User name of Gmail account
    :param password: Password
    :param dest_dir: Destination directory root where the files will be imported
    :return: Error code 0 = Ok, otherwise Nok
    :return: attach_dir final destination directory
    """

    # Configure logging
    logging.basicConfig(filename=os.path.join(dest_dir, 'attach.log'), level=logging.INFO)

    # IMAP Settings
    host = 'imap.gmail.com'

    # Create directory
    attach_dir = os.path.join(dest_dir, 'attachments')
    if not os.path.isdir(attach_dir):
        os.mkdir(attach_dir)

    logging.info(f'Destination directory is {attach_dir}')

    try:
        # Create the IMAP Client
        imap = imaplib.IMAP4_SSL(host=host) # TODO: IMAP connection securely and properly

        # Login to the IMAP server
        resp, data = imap.login(user, password)

        # Check login
        if resp == 'OK':
            logging.info(f'Login to {user}@gmail.com successful.')
        else:
            raise ValueError('Not able to log in !')

        # Get folder name based on Gmail flag
        folder = get_folder(imap=imap, flag='All')

        resp, data = imap.list(f'{folder}', '*')
        if resp != 'OK':
            logging.warning(f'No mailboxes found in directory {folder}')
            return -1, None

        else:
            # Select folder to treat
            imap.select(f'{folder}', True)

            # Get all message numbers
            resp, msg_ids = imap.search(None, 'ALL')
            msg_count = len(msg_ids[0].split())
            logging.info(f'Number of messages to read is {msg_count}.')

            for msg_id in msg_ids[0].split():
                resp, data = imap.fetch(msg_id, '(RFC822)')
                raw_email = data[0][1]
                mail = email.message_from_string(raw_email.decode('utf-8'))
                # mail = email.message_from_bytes(raw_email)

                for part in mail.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue

                    file_name = part.get_filename()

                    if bool(file_name):
                        if not os.path.isfile(os.path.join(attach_dir, file_name)):
                            try:
                                i = 0
                                base_name, ext = os.path.splitext(file_name)
                                file_path = os.path.join(attach_dir, f'{base_name}_{i}{ext}')

                                while os.path.exists(file_path):
                                    i += 1
                                    file_path = os.path.join(attach_dir, f'{base_name}_{i}{ext}')

                                fp = open(file_path, 'wb')
                                fp.write(part.get_payload(decode=True))
                                fp.close()

                                logging.debug(f'{base_name}_{i}{ext}' + ' imported.')

                            except:
                                logging.warning('Could not import attachment: ' + file_name.replace('\n', ' ').replace('\r', ''))

            return 0, attach_dir

    except ValueError as e:
        logging.error(e)
        return -1, None

    except:
        logging.error(f'Unexpected error : {sys.exc_info()[0]}')
        logging.error(traceback.format_exc())
        return -1, None

    finally:
        # TODO: debug if this code is executed even if return is called
        if imap is not None:
            imap.close()
            imap.logout()


# Debug purposes
# if __name__ == '__main__':
#     aux1, aux2 = download_attachments(user='albert.rodriguez.lopez'
#                                       , password='******'
#                                       , dest_dir='.')
