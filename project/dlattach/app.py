import os

# from dlattach.common import attach
from dlattach.common import gmail_api, org
from datetime import datetime


def main(user_name, password):
    """
    Download and organize all attachments of a Gmail account
    :return: Error code 0 = Ok, otherwise Nok
    :return: Error message
    """

    # Get destination directory
    current_path = os.path.realpath(__file__)
    dest_dir = os.path.join(current_path, 'resources', datetime.now().strftime("%Y%m%d-%H%M"))

    # Create directories
    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)

    # TODO: get password and username correctly
    attach_resp, attach_dir = attach.download_attachments(user_name=user_name, passwd=password, dest_dir=dest_dir)

    # Organise files into directories by extension
    if attach_resp == 0:
        org_resp = org.by_type(src_dir=attach_dir, dest_dir=dest_dir)

    if attach_resp != 0:
        return -1, 'Attachments could not be downloaded. Check attach.log file for further details.'

    if org_resp != 0:
        return -1, 'Files could not be organized. Check org.log for further details.'


if __name__ == '__main__':
    resp, msg = main(user_name='gmail-user', password='gmail-password')