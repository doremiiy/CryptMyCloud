import json
import os
import tkinter as tk
from tkinter.filedialog import askopenfilename

import requests

import file_manager


SETTINGS = {}


class FileInterface(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.file_list = tk.Listbox(self)
        self.file_list.grid(rowspan=3, column=0)
        tk.Button(self, text='Upload new file', command=self.upload_file).grid(row=0, column=1)
        tk.Button(self, text='Delete', command=self.delete_file).grid(row=1, column=1)
        tk.Button(self, text='Download & Decrypt', command=self.upload_file).grid(row=2, column=1)
        self.error_message = tk.Label(self, text='', fg='red')
        self.error_message.grid(row=2, column=0)
        self.refresh_list()

    def refresh_list(self):
        try:
            result = requests.get(
                'http://%s:%s/file/list/' % (SETTINGS['SERVER_IP'], SETTINGS['SERVER_PORT']),
                headers={'Authorization': 'JWT % s' % self.parent.jwt_token}
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

    def upload_file(self):
        file_obj = askopenfilename()
        if not file_obj:
            return
        file_name = os.path.basename(file_obj)
        try:
            result = requests.post(
                'http://%s:%s/file/' % (SETTINGS['SERVER_IP'], SETTINGS['SERVER_PORT']),
                data={'file_name': file_name},
                headers={'Authorization': 'JWT %s' % self.parent.jwt_token}
            )
        except requests.exceptions.RequestException:
            self.error_message.config(text='No internet connection!')
            return

        if result.status_code == requests.codes.created:
            self.error_message.config(text='')
            os.makedirs('temp')
            file_manager.encrypt(
                file_obj,
                'temp/%s' % file_name,
                bytes.fromhex(result.json()['key'])
            )
            # TODO: Upload TempFile to google drive
            # os.system('rm -rf temp')
            self.refresh_list()
        else:
            self.error_message.config(text='Http error : %d' % result.status_code)

    def delete_file(self):
        try:
            indexes = self.file_list.curselection()
            for index in indexes:
                try:
                    requests.delete(
                        'http://%s:%s/file/' % (SETTINGS['SERVER_IP'], SETTINGS['SERVER_PORT']),
                        params={'file_name': self.file_list.get(index)},
                        headers={'Authorization': 'JWT %s' % self.parent.jwt_token}
                    )
                except requests.exceptions.RequestException:
                    pass
                self.file_list.delete(index)
        except IndexError:
            pass
        self.refresh_list()

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
                'http://%s:%s/api-token-auth/' % (SETTINGS['SERVER_IP'], SETTINGS['SERVER_PORT']),
                json={'username': self.email.get(), 'password': self.password.get()}
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
            FileInterface(self.parent).grid()
        else:
            self.error_message.config(text='Http error : %d' % result.status_code)


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title('CryptMyCloud - PythonClient')

        need_login = True
        self.jwt_token = None

        if SETTINGS.get('JWT_TOKEN'):
            try:
                result = requests.post(
                    'http://%s:%s/api-token-refresh/' % (
                    SETTINGS['SERVER_IP'], SETTINGS['SERVER_PORT']),
                    json={'token': SETTINGS['JWT_TOKEN']}
                )
            except requests.exceptions.RequestException:
                result = None
            if result and result.status_code == 200:
                self.jwt_token = result.json().get('token')
                SETTINGS['JWT_TOKEN'] = self.jwt_token
                with open('settings.json', 'w') as settings_file:
                    json.dump(SETTINGS, settings_file)
                need_login = False
                FileInterface(self.parent).grid()

        if need_login:
            LoginInterface(self.parent).grid()


if __name__ == "__main__":
    with open('settings.json', 'r') as settings_file:
        SETTINGS = json.load(settings_file)
    root = tk.Tk()
    root.minsize(width=SETTINGS['WIDTH'], height=SETTINGS['HEIGHT'])

    MainApplication(root).grid(row=1, column=1)

    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(2, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(2, weight=1)

    root.mainloop()
