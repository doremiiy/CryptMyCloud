import os

import paramiko


SERVER_ADDR = 'tuxa.sme.utc'
SERVER_PORT = 22
BASE_PATH = '/volsme/user1x/users/rv01a003/CryptMyCloud/%s'

transport = paramiko.Transport((SERVER_ADDR, SERVER_PORT))
transport.connect(username='rv01a003', password='tmmZP8kC')
sftp = paramiko.SFTPClient.from_transport(transport)

def upload(file_obj):
    sftp.put('%s' % file_obj, BASE_PATH % os.path.basename(file_obj))


def download(file_name, output_directory):
    sftp.get(BASE_PATH % file_name, '%s/%s' % (output_directory, file_name))


def delete(file_name):
    sftp.remove(BASE_PATH % file_name)
