import json
import os
import tempfile
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename

import requests

import cloud_manager
import file_manager

SETTINGS = {}


class ShareFileInterface(tk.Toplevel):
    def __init__(self, parent, file_name, *args, **kwargs):
        tk.Toplevel.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.file_name = file_name

        tk.Label(self, text='Share "%s" with:' % self.file_name).pack()
        self.user_list = tk.Listbox(self, selectmode=tk.MULTIPLE)
        self.user_list.pack()
        tk.Button(self, text='Share', command=self.share).pack()

        try:
            all_user = requests.get(
                '%s/user/list/' % SETTINGS['SERVER_URL'],
                headers={'Authorization': 'JWT % s' % self.parent.jwt_token},
                verify=False
            )
        except requests.exceptions.RequestException:
            self.parent.reset_error_message('Cannot contact server')
        else:
            try:
                authorised_users = requests.get(
                    '%s/file/' % SETTINGS['SERVER_URL'],
                    params={'file_name': self.file_name},
                    headers={'Authorization': 'JWT %s' % self.parent.jwt_token},
                    verify=SETTINGS['SSL_CERTIFICATE_VERIFICATION']
                )
            except requests.exceptions.RequestException:
                self.parent.reset_error_message('Cannot contact server')
            else:
                if all_user.status_code != requests.codes.ok:
                    self.parent.print_error_message(all_user)
                elif authorised_users.status_code != requests.codes.ok:
                    self.parent.print_error_message(authorised_users)
                else:
                    for user in all_user.json():
                        self.user_list.insert(tk.END, user['username'])
                        if user['username'] in authorised_users.json().get('allowed_user', []):
                            self.user_list.selection_set(tk.END)

    def share(self):
        self.parent.reset_error_message()
        user_names = [self.user_list.get(index) for index in self.user_list.curselection()]
        try:
            result = requests.patch(
                '%s/file/' % SETTINGS['SERVER_URL'],
                params={'file_name': self.file_name},
                data={'allowed_user': user_names},
                headers={'Authorization': 'JWT %s' % self.parent.jwt_token},
                verify=SETTINGS['SSL_CERTIFICATE_VERIFICATION']
            )
        except requests.exceptions.RequestException:
            self.parent.reset_error_message('Cannot contact server')
        if result.status_code != requests.codes.ok:
            self.parent.print_error_message(result)
        self.destroy()


class FileInterface(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.file_list = ttk.Treeview(self)
        self.file_list['columns'] = ('owner',)
        self.file_list.heading('#0', text='File Name', anchor='w')
        self.file_list.heading('owner', text='Owner', anchor='w')
        self.file_list.column('#0', anchor='center', width=500)
        self.file_list.column('owner', anchor='center', width=100)
        self.file_list.grid(rowspan=3, column=0)
        tk.Button(
            self,
            text='Cipher & Upload new file',
            command=self.cipher_upload_file
        ).grid(row=0, column=1)
        tk.Button(self, text='Share File', command=self.share_file).grid(row=1, column=1)
        tk.Button(self, text='Delete file', command=self.delete_file).grid(row=2, column=1)
        tk.Button(
            self,
            text='Download & Decipher',
            command=self.download_decipher_file
        ).grid(row=3, column=1)
        self.refresh_list()

    def refresh_list(self):
        try:
            result = requests.get(
                '%s/file/list/' % SETTINGS['SERVER_URL'],
                headers={'Authorization': 'JWT % s' % self.parent.jwt_token},
                verify=False
            )
        except requests.exceptions.RequestException:
            self.parent.reset_error_message('Cannot contact server')
            return
        if result.status_code == requests.codes.ok:
            self.file_list.delete(*self.file_list.get_children())
            for file_obj in result.json():
                self.file_list.insert(
                    '',
                    tk.END,
                    text=file_obj['file_name'],
                    value=file_obj['owner']
                )
        else:
            self.parent.print_error_message(result)

    def cipher_upload_file(self):
        self.parent.reset_error_message()
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
            self.parent.reset_error_message('Cannot contact server')
            return

        if result.status_code == requests.codes.created:
            with tempfile.TemporaryDirectory() as temp_directory:
                file_manager.encrypt(
                    file_obj,
                    '%s/%s' % (temp_directory, file_name),
                    bytes.fromhex(result.json()['key'])
                )
                cloud_manager.upload('%s/%s' % (temp_directory, file_name))
            self.refresh_list()
        else:
            self.parent.print_error_message(result)

    def delete_file(self):
        self.parent.reset_error_message()
        items = self.file_list.selection()
        if not items:
            self.parent.reset_error_message('Select one file')
        for item in items:
            try:
                result = requests.delete(
                    '%s/file/' % SETTINGS['SERVER_URL'],
                    params={'file_name': self.file_list.item(item, 'text')},
                    headers={'Authorization': 'JWT %s' % self.parent.jwt_token},
                    verify=SETTINGS['SSL_CERTIFICATE_VERIFICATION']
                )
            except requests.exceptions.RequestException:
                self.parent.reset_error_message('Cannot contact server')
            else:
                if result.status_code == requests.codes.no_content:
                    cloud_manager.delete(self.file_list.item(item, 'text'))
                else:
                    self.parent.print_error_message(result)
        self.refresh_list()

    def download_decipher_file(self):
        self.parent.reset_error_message()
        items = self.file_list.selection()
        if not items:
            self.parent.reset_error_message('Select one file')
        for item in items:
            file_name = self.file_list.item(item, 'text')
            try:
                result = requests.get(
                    '%s/file/' % SETTINGS['SERVER_URL'],
                    params={'file_name': file_name},
                    headers={'Authorization': 'JWT %s' % self.parent.jwt_token},
                    verify=SETTINGS['SSL_CERTIFICATE_VERIFICATION']
                )
            except requests.exceptions.RequestException:
                self.parent.reset_error_message('Cannot contact server')
            if result.status_code == requests.codes.ok:
                with tempfile.TemporaryDirectory() as temp_directory:
                    cloud_manager.download(file_name, temp_directory)
                    file_manager.decrypt(
                        '%s/%s' % (temp_directory, file_name),
                        'Output/%s' % file_name,
                        bytes.fromhex(result.json()['key'])
                    )
            else:
                self.parent.print_error_message(result)

    def share_file(self):
        self.parent.reset_error_message()
        items = self.file_list.selection()
        if not items:
            self.parent.reset_error_message('Select one file')
            return
        for item in items:
            ShareFileInterface(self.parent, self.file_list.item(item, 'text'))


class LoginInterface(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.stay_logged = tk.IntVar()

        tk.Label(self, text='username').grid(row=0, column=0, sticky=tk.W)
        tk.Entry(self, textvariable=self.username).grid(row=0, column=1, sticky=tk.E)
        tk.Label(self, text='password').grid(row=1, column=0, sticky=tk.W)
        password_field = tk.Entry(self, textvariable=self.password)
        password_field.config(show="*")
        password_field.grid(row=1, column=1, sticky=tk.E)
        tk.Checkbutton(self, text='Stay logged', variable=self.stay_logged).grid(row=2, column=0)
        tk.Button(self, text='Log In', command=self.login).grid(row=2, column=1)

    def login(self):
        self.parent.reset_error_message()
        if not self.username.get() or not self.password.get():
            self.parent.reset_error_message('Empty field!')
            return
        try:
            result = requests.post(
                '%s/api-token-auth/' % SETTINGS['SERVER_URL'],
                json={'username': self.username.get(), 'password': self.password.get()},
                verify=SETTINGS['SSL_CERTIFICATE_VERIFICATION']
            )
        except requests.exceptions.RequestException:
            self.parent.reset_error_message('Cannot contact server')
            return

        if result.status_code == requests.codes.ok:
            self.parent.jwt_token = result.json().get('token')
            if self.stay_logged.get():
                SETTINGS['JWT_TOKEN'] = self.parent.jwt_token
                with open('settings.json', 'w') as settings:
                    json.dump(SETTINGS, settings)
            self.grid_forget()
            FileInterface(self.parent).grid(row=1, column=1)
        else:
            self.parent.print_error_message(result)


class MainApplication(tk.Tk):
    def __init__(self):
        super(MainApplication, self).__init__()
        self.title('CryptMyCloud - PythonClient')
        self.minsize(width=SETTINGS['WIDTH'], height=SETTINGS['HEIGHT'])
        self.grid_rowconfigure(0, weight=1)
        self.error_message = tk.Label(self, text='', fg='red')
        self.error_message.grid(row=3, column=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        need_login = True
        self.jwt_token = None

        if SETTINGS.get('JWT_TOKEN'):
            try:
                result = requests.post(
                    '%s/api-token-refresh/' % SETTINGS['SERVER_URL'],
                    json={'token': SETTINGS['JWT_TOKEN']},
                    verify=False
                )
            except requests.exceptions.RequestException:
                pass
            else:
                if result.status_code == requests.codes.ok:
                    self.jwt_token = result.json().get('token')
                    SETTINGS['JWT_TOKEN'] = self.jwt_token
                    with open('settings.json', 'w') as settings:
                        json.dump(SETTINGS, settings)
                    need_login = False
                    FileInterface(self).grid(row=1, column=1)


        if need_login:
            LoginInterface(self).grid(row=1, column=1)

    def print_error_message(self, response):
        def flat_list(my_list):
            result = []
            for element in my_list:
                if isinstance(element, list):
                    result.extend(flat_list(element))
                else:
                    result.append(element)
            return result

        error_list = flat_list(list(response.json().values()))
        self.error_message.config(text='\n'.join(error_list))

    def reset_error_message(self, text=''):
        self.error_message.config(text=text)


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning
    )
    with open('settings.json', 'r') as settings_file:
        SETTINGS = json.load(settings_file)
    MainApplication().mainloop()
