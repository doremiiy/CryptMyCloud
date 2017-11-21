import os


def upload(file_obj):
    os.system('cp %s Cloud/%s' % (file_obj, os.path.basename(file_obj)))


def download(file_name):
    os.system('cp Cloud/%s temp/%s' % (file_name, file_name))


def delete(file_name):
    os.system('rm -f Cloud/%s' % file_name)