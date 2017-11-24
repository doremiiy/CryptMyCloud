import json
import os
import tempfile
import tkinter as tk
from tkinter.filedialog import askopenfilename

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import cloud_manager
import file_manager


SETTINGS = {}


class FileInterface(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.file_list = tk.Listbox(self)
        self.file_list.grid(rowspan=3, column=0)
        tk.Button(
            self,
            text='Cipher & Upload new file',
            command=self.cipher_upload_file
        ).grid(row=0, column=1)
        tk.Button(self, text='Delete file', command=self.delete_file).grid(row=1, column=1)
        tk.Button(
            self,
            text='Download & Decipher',
            command=self.download_decipher_file
        ).grid(row=2, column=1)
        self.error_message = tk.Label(self, text='', fg='red')
        self.error_message.grid(row=2, column=0)
        self.refresh_list()

    def refresh_list(self):
        try:
            result = requests.get(
                '%s/file/list/' % SETTINGS['SERVER_URL'],
                headers={'Authorization': 'JWT % s' % self.parent.jwt_token},
                verify=False
            )
        except requests.exceptions.RequestException:
            self.error_message.config(text='No internet connection!')
            return
        if result.status_code == requests.codes.ok:
            self.file_list.delete(0, self.file_list.size()-1)
            self.error_message.config(text='')
            for file_obj in result.json():
                self.file_list.insert(tk.END, file_obj['file_name'])
        else:
            self.error_message.config(text='Http error : %d' % result.status_code)

    def cipher_upload_file(self):
        file_obj = askopenfilename()
        if not file_obj:
            return
        file_name = os.path.basename(file_obj)
        try:
            result = requests.post(
                '%s/file/' % SETTINGS['SERVER_URL'],
                data={'file_name': file_name},
                headers={'Authorization': 'JWT %s' % self.parent.jwt_token},
                verify=SETTINGS['SSL_CERTIFICATE_VERIFICATION']
            )
        except requests.exceptions.RequestException:
            self.error_message.config(text='No internet connection!')
            return

        if result.status_code == requests.codes.created:
            self.error_message.config(text='')
            with tempfile.TemporaryDirectory() as temp_directory:
                file_manager.encrypt(
                    file_obj,
                    '%s/%s' % (temp_directory, file_name),
                    bytes.fromhex(result.json()['key'])
                )
                cloud_manager.upload('%s/%s' % (temp_directory, file_name))
            self.refresh_list()
        else:
            self.error_message.config(text='Http error : %d' % result.status_code)

    def delete_file(self):
        try:
            indexes = self.file_list.curselection()
            for index in indexes:
                try:
                    requests.delete(
                        '%s/file/' % SETTINGS['SERVER_URL'],
                        params={'file_name': self.file_list.get(index)},
                        headers={'Authorization': 'JWT %s' % self.parent.jwt_token},
                        verify=SETTINGS['SSL_CERTIFICATE_VERIFICATION']
                    )
                except requests.exceptions.RequestException:
                    pass
                cloud_manager.delete(self.file_list.get(index))
                self.file_list.delete(index)
        except IndexError:
            pass
        self.refresh_list()

    def download_decipher_file(self):
        try:
            indexes = self.file_list.curselection()
            for index in indexes:
                file_name = self.file_list.get(index)
                try:
                    result = requests.get(
                        '%s/file/' % SETTINGS['SERVER_URL'],
                        params={'file_name': file_name},
                        headers={'Authorization': 'JWT %s' % self.parent.jwt_token},
                        verify=SETTINGS['SSL_CERTIFICATE_VERIFICATION']
                    )
                except requests.exceptions.RequestException:
                    pass
                if result.status_code == requests.codes.ok:
                    with tempfile.TemporaryDirectory() as temp_directory:
                        cloud_manager.download(file_name, temp_directory)
                        file_manager.decrypt(
                            '%s/%s' % (temp_directory, file_name),
                            'Output/%s' % file_name,
                            bytes.fromhex(result.json()['key'])
                        )
        except IndexError:
            pass


class LoginInterface(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.email = tk.StringVar()
        self.password = tk.StringVar()
        self.stay_logged = tk.IntVar()

        self.error_message = tk.Label(self, text='', fg='red')

        tk.Label(self, text='email').grid(row=0, column=0, sticky=tk.W)
        tk.Entry(self, textvariable=self.email).grid(row=0, column=1, sticky=tk.E)
        tk.Label(self, text='password').grid(row=1, column=0, sticky=tk.W)
        password_field = tk.Entry(self, textvariable=self.password)
        password_field.config(show="*")
        password_field.grid(row=1, column=1, sticky=tk.E)
        tk.Checkbutton(self, text='Stay logged', variable=self.stay_logged).grid(row=2, column=0)
        tk.Button(self, text='Log In', command=self.login).grid(row=2, column=1)
        self.error_message.grid(row=3, columnspan=2)

    def login(self):
        if not self.email.get() or not self.password.get():
            self.error_message.config(text='Empty field!')
            return 
        try:
            result = requests.post(
                '%sapi-token-auth/' % SETTINGS['SERVER_URL'],
                json={'username': self.email.get(), 'password': self.password.get()},
                verify=SETTINGS['SSL_CERTIFICATE_VERIFICATION']
            )
        except requests.exceptions.RequestException:
            self.error_message.config(text='No internet connection!')
            return

        if result.status_code == requests.codes.ok:
            self.parent.jwt_token = result.json().get('token')
            if self.stay_logged.get():
                SETTINGS['JWT_TOKEN'] = self.parent.jwt_token
                with open('settings.json', 'w') as settings_file:
                    json.dump(SETTINGS, settings_file)
            self.grid_forget()
            FileInterface(self.parent).grid(row=1, column=1)
        else:
            self.error_message.config(text='Http error : %d' % result.status_code)


class MainApplication(tk.Tk):

    def __init__(self):
        super(MainApplication, self).__init__()
        self.title('CryptMyCloud - PythonClient')
        self.minsize(width=SETTINGS['WIDTH'], height=SETTINGS['HEIGHT'])
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        need_login = True
        self.jwt_token = None

        if SETTINGS.get('JWT_TOKEN'):
            try:
                result = requests.post(
                    '%s/api-token-refresh/'% SETTINGS['SERVER_URL'],
                    json={'token': SETTINGS['JWT_TOKEN']},
                    verify=False
                )
            except requests.exceptions.RequestException:
                pass
            else:
                if result.status_code == requests.codes.ok:
                    self.jwt_token = result.json().get('token')
                    SETTINGS['JWT_TOKEN'] = self.jwt_token
                    with open('settings.json', 'w') as settings_file:
                        json.dump(SETTINGS, settings_file)
                    need_login = False
                    FileInterface(self).grid(row=1, column=1)

        if need_login:
            LoginInterface(self).grid(row=1, column=1)


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    with open('settings.json', 'r') as settings_file:
        SETTINGS = json.load(settings_file)
    MainApplication().mainloop()
