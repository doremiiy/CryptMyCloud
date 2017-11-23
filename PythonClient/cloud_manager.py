import os
import shutil


def upload(file_obj):
    shutil.copyfile('%s' % file_obj, 'Cloud/%s' % os.path.basename(file_obj))


def download(file_name, output_directory):
    shutil.copyfile('Cloud/%s' % file_name, '%s/%s' % (output_directory, file_name))


def delete(file_name):
    os.remove('Cloud/%s' % file_name)