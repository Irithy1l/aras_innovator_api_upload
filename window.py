import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog, scrolledtext, messagebox
import threading

import requests
import sv_ttk
import time

import structure.bom as bom
import connection.generate_token as generate_token
import connection.search as search
import connection.download_file as download_file
import login.user_info as user_info

from exception.error import EmptyFileError
from exception.error import UploadFinish
from exception.error import InsufficientPermissionsError
from exception.error import SkipExist


class BeautifulGUI(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("百工汇智PDM拓展程序————未登录")
        self.geometry("540x530")

        self.iconbitmap('cover.ico')

        self.username = ''
        self.password = ''
        self.login_verified = False

        self.hide = True

        self.token = None

        self.running = False

        # self.create_menu()
        self.create_intro()
        self.create_widgets()
        self.create_upload_history()

        sv_ttk.use_light_theme()

        self.overwrite = True

    def create_menu(self):
        menubar = tk.Menu(self)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="选择文件夹", command=self.select_folder)
        file_menu.add_separator()
        file_menu.add_command(label="清空页面", command=self.clear_folder)
        file_menu.add_command(label="退出", command=self.quit)
        menubar.add_cascade(label="文件", menu=file_menu)

        login_menu = tk.Menu(menubar, tearoff=0)
        login_menu.add_command(label="用户登录", command=self.open_login_window)
        menubar.add_cascade(label="登录", menu=login_menu)


        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)

        self.config(menu=menubar)

    def show_about(self):
        """Display 'About' information"""
        messagebox.showinfo(title="About", message="This is a directory structure upload tool.")

    def on_focus_in_username(self, event):
        if self.username_input.get() == '用户名':
            self.username_input.delete(0, tk.END)
            self.username_input.insert(0, '')
            self.username_input.config(foreground='black')

    def on_focus_out_username(self, event):
        if self.username_input.get() == '':
            self.username_input.insert(0, '用户名')
            self.username_input.config(foreground='grey')

    def on_focus_in_password(self, event):
        if self.password_input.get() == '密码':
            self.password_input.delete(0, tk.END)
            self.password_input.insert(0, '')
            self.password_input.config(foreground='black')
            if self.hide:
                self.password_input.config(show='*')
            else:
                self.password_input.config(show='')

    def on_focus_out_password(self, event):
        if self.password_input.get() == '':
            self.password_input.config(show='')
            self.password_input.insert(0, '密码')
            self.password_input.config(foreground='grey')

    def open_login_window(self):
        self.login_window = tk.Tk()
        self.login_window.wm_title('用户登录')
        self.login_window.geometry('326x250')
        self.login_window.iconbitmap('cover.ico')
        self.login_window.attributes('-topmost', 'true')
        self.login_window.resizable(width=False, height=False)
        self.hide = True

        # self.username_label = ttk.Label(login_window, text="用户名:")
        # self.username_label.grid(row=0, column=0, pady=5, padx=5, sticky='W')

        login_frame = ttk.Frame(self.login_window)
        login_frame.grid(row=0, column=0, padx=50, pady=40)

        self.username_input = ttk.Entry(login_frame, foreground='grey', width=25)
        self.username_input.grid(row=0, column=0, columnspan=2, pady=5, padx=20, sticky='WE')
        self.username_input.bind('<FocusIn>', self.on_focus_in_username)
        self.username_input.bind('<FocusOut>', self.on_focus_out_username)
        self.username_input.insert(0, '用户名')

        # self.password_label = ttk.Label(login_window, text="密码:")
        # self.password_label.grid(row=1, column=0, pady=5, padx=5, sticky='W')

        self.password_input = ttk.Entry(login_frame, show='*', width=22)
        self.password_input.grid(row=1, column=0, columnspan=2, pady=5, padx=20, sticky='W')
        self.password_input.bind('<FocusIn>', self.on_focus_in_password)
        self.password_input.bind('<FocusOut>', self.on_focus_out_password)
        self.password_input.config(show='')
        self.password_input.insert(0, '密码')
        self.password_input.config(foreground='grey')

        self.invisible = tk.PhotoImage(master=self.login_window, file='可见性-不可见.png')
        self.visible = tk.PhotoImage(master=self.login_window, file='可见性-可见.png')

        self.show_button = ttk.Button(login_frame, image=self.invisible, command=self.change_show,
                                      width=5)
        self.show_button.grid(row=1, column=1, sticky='E', padx=20)

        self.auto_state = tk.BooleanVar(self.login_window, value=False)
        self.auto_login = ttk.Checkbutton(login_frame, text="自动登录", variable=self.auto_state)
        self.auto_login.grid(row=2, column=0, padx=20)

        self.remember_state = tk.BooleanVar(self.login_window, value=True)
        self.remember_password = ttk.Checkbutton(login_frame, text="记住密码", variable=self.remember_state)
        self.remember_password.grid(row=2, column=1, padx=20)

        self.login_button_window = tk.Button(login_frame, text="登录", command=self.login_test, background='#169BD5')
        self.login_button_window.grid(row=3, column=0, columnspan=2, sticky='WE', padx=20, pady=10)

        self.get_recent_user()

        if self.auto_state.get():
            self.login_test()

    def get_recent_user(self):
        self.user_list = user_info.UserList('login/username_pwd.txt')
        recent_user = None
        for username, user in self.user_list.user_list.items():
            if recent_user is None:
                recent_user = user
            else:
                if user.login_date > recent_user.login_date:
                    recent_user = user

        if recent_user:
            self.username_input.delete(0, tk.END)
            self.username_input.config(foreground='black')
            self.username_input.insert(0, recent_user.username)
            if recent_user.password != 'N/A':
                self.password_input.delete(0, tk.END)
                self.password_input.config(foreground='black')
                self.password_input.config(show='*')
                self.password_input.insert(0, recent_user.password)
            elif recent_user.password == 'N/A':
                self.remember_state.set(False)

            if recent_user.auto_login == '1':
                self.auto_state.set(True)

    def create_intro(self):

        self.intro = ttk.Frame(self)

        self.intro_header = ttk.Label(self.intro, text='操作流程')
        self.intro_header.grid(row=0, column=0, padx=10, pady=5, sticky='W')

        self.first_line = ttk.Label(self.intro, text='1. 请在上方使用Aras Innovator账号登录')
        self.first_line.grid(row=1, column=0, padx=5, pady=5, sticky='W')

        self.second_line = ttk.Label(self.intro, text='2. 请点击后方按钮选择文件夹路径')
        self.second_line.grid(row=2, column=0, padx=5, pady=5, sticky='W')

        self.third_line = ttk.Label(self.intro, text='3. 请点击后方按钮开始上传文件')
        self.third_line.grid(row=3, column=0, padx=5, pady=5, sticky='W')

        self.fourth_line = ttk.Label(self.intro, text='4. 零部件上传完成')
        self.fourth_line.grid(row=4, column=0, padx=5, pady=10, sticky='W')

        self.login_button = tk.Button(self.intro, text="登录", command=self.open_login_window, background='#169BD5')
        self.login_button.grid(row=1, column=1, padx=5, pady=5, sticky='W')

        self.select_folder_button = tk.Button(self.intro, text="选择文件夹", command=self.select_folder, state='disabled')
        self.select_folder_button.grid(row=2, column=1, padx=5, pady=5, sticky='W')

        self.run_button = tk.Button(self.intro, text="上传", command=self.run_function, state='disabled')
        self.run_button.grid(row=3, column=1, padx=5, pady=5, sticky='W')

        self.intro.grid(row=0, column=0, sticky='WE')



    def create_widgets(self):

        # login_frame = ttk.Frame(self)
        # login_frame.pack(pady=5, fill=tk.X)
        #
        # self.username_label = ttk.Label(login_frame, text="用户名:")
        # self.username_label.pack(side=tk.LEFT, padx=5)
        #
        # self.username_input = ttk.Entry(login_frame)
        # self.username_input.pack(side=tk.LEFT, padx=5)
        #
        # self.password_label = ttk.Label(login_frame, text="密码:")
        # self.password_label.pack(side=tk.LEFT, padx=10)
        #
        # self.password_input = ttk.Entry(login_frame, show='*')
        # self.password_input.pack(side=tk.LEFT, padx=5)
        #
        # self.show_button = ttk.Button(login_frame, text='显示/隐藏密码', command=self.change_show)
        # self.show_button.pack(side=tk.LEFT)
        #
        # self.login_button = ttk.Button(login_frame, text="登录", command=self.login)
        # self.login_button.pack(side=tk.LEFT, padx=20)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, padx=5, sticky='WENS')

        setattr(self, 'progress', ttk.Frame(self.notebook))
        self.notebook.add(getattr(self, 'progress'), text='上传进度')

        setattr(self, 'history', ttk.Frame(self.notebook))
        self.notebook.add(getattr(self, 'history'), text='历史记录')

        output_frame = ttk.Frame(self.progress)
        output_frame.grid(row=2, column=0, sticky='WE')

        folder_frame = ttk.Frame(output_frame)
        folder_frame.grid(row=0, column=0, pady=10)

        self.folder_header = ttk.Label(folder_frame, text='文件夹路径')
        self.folder_header.grid(row=0, column=0, sticky='W', padx=5)

        self.folder_textbox = ttk.Entry(folder_frame, width=70)
        self.folder_textbox.grid(row=1, column=0, padx=5, pady=5, sticky='WE')

        progress_frame = ttk.Frame(output_frame)
        progress_frame.grid(row=1, column=0, sticky='WE')

        self.progress = tk.StringVar()
        self.progress.set('进度: 未开始上传')
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress, justify=tk.RIGHT)
        self.progress_label.pack(side=tk.LEFT, padx=5)


        self.progress_bar = ttk.Progressbar(progress_frame, orient='horizontal', length=200, mode='determinate')
        self.progress_bar.pack(side=tk.RIGHT, padx=5, pady=5)

        self.file_progress = tk.StringVar()
        self.file_progress.set('0/0')
        self.file_progress_label = ttk.Label(progress_frame, textvariable=self.file_progress)
        self.file_progress_label.pack(side=tk.RIGHT, padx=5, pady=5)

        self.output = tk.StringVar()
        self.output_textbox = scrolledtext.ScrolledText(output_frame, width=70, height=15)
        self.output_textbox.grid(row=2, column=0, pady=5)
        self.output_textbox.focus()

    # def change_show_thread_job(self):
    #     if self.hide:
    #         self.password_input.configure(show='')
    #         self.hide = False
    #     else:
    #         self.password_input.configure(show='*')
    #         self.hide = True

    def create_upload_history(self):
        self.history_label = ttk.Label(self.history, text='已上传零部件')
        self.history_label.grid(row=0, column=0, padx=5, pady=10, sticky='W')

        self.refresh_history_button = ttk.Button(self.history, text='刷新', command=self.on_click_refresh_button)
        self.refresh_history_button.grid(row=0, column=1, padx=5, pady=10, sticky='W')

        self.history_frame = ttk.Frame(self.history)
        self.history_frame.grid(row=1, column=0, columnspan=2, sticky='WESN')

        self.scrollbar = ttk.Scrollbar(self.history_frame)
        self.scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            self.history_frame,
            columns=(1, 2, 3),
            height=11,
            selectmode="browse",
            show=("tree",),
            yscrollcommand=self.scrollbar.set,
        )
        self.scrollbar.config(command=self.tree.yview)
        self.tree.pack(expand=True, padx=5, fill="both")

        # 总宽度为 475
        self.tree.column("#0", anchor="w", width=90)
        self.tree.column(1, anchor="w", width=165)
        self.tree.column(2, anchor="w", width=80)
        self.tree.column(3, anchor="w", width=150)
        self.tree.bind('<Double-1>', self.test)


        # self.part_list = download_file.get_part(self.id, self.token)
        #
        # tree_data = [
        #     *[("", x, self.part_list[x - 1][0], (self.part_list[x - 1][2], self.part_list[x - 1][3])) for x in range(1, len(self.part_list) + 1)],
        # ]
        #
        # for item in tree_data:
        #     parent, iid, text, values = item
        #     print(item)
        #     self.tree.insert(parent=parent, index="end", iid=iid, text=text, values=values)

        # with open('upload_history.txt', 'r') as file:
        #     lines = file.readlines()
        #     for line in lines:
        #         print(line)
        #         temp = (file_name, file_id, file_date, file_time) = line.split(sep='&&')
        #         temp[3] = temp[3][:-1]
        #         self.part_list.append(temp)
        #     print(self.part_list)

            # if not parent or iid in {8, 21}:
            #     self.tree.item(iid, open=True)

        # self.tree.selection_set(14)
        # self.tree.see(7)


    def get_uploaded(self):
        url = 'http://47.96.66.12/InnovatorServer/Server/odata/CAD'
        headers = {'Authorization': self.token}




    def test(self, event):
        print(self.tree.focus(), self.part_list[int(self.tree.focus()) - 1])

    def change_show(self):
        """修改密码的显示和隐藏"""

        # change_show_thread = threading.Thread(target=self.change_show_thread_job)
        # change_show_thread.start()

        if self.hide:
            if self.password_input.get() != '密码':
                self.password_input.configure(show='')
            self.hide = False
            self.show_button.config(image=self.visible)
        else:
            if self.password_input.get() != '密码':
                self.password_input.configure(show='*')
            self.hide = True
            self.show_button.config(image=self.invisible)

    def stop_function(self):
        """终止目录结构上传"""

        self.running = False

    # def login_thread_job(self):
    #     """验证输入的用户名和密码是否可以用于登录，若可以"""
    #     self.token = generate_token.generate(self.username_input.get(), self.password_input.get())
    #     if self.token is None:
    #         messagebox.showerror(title='登录失败', message='用户名或密码错误')
    #         self.login_verified = False
    #     else:
    #         messagebox.showinfo(title='登录成功', message='登录成功')
    #
    #         self.token = f'Bearer {self.token}'
    #
    #         self.username = self.username_input.get()
    #         self.password = self.password_input.get()
    #         self.login_verified = True

    def login_test(self):

        self.token = generate_token.generate(self.username_input.get(), self.password_input.get())
        if self.token is None:
            messagebox.showerror(title='登录失败', message='用户名或密码错误')
            self.login_verified = False
            self.title(f'百工汇智PDM拓展程序————未登录')
            self.select_folder_button.config(state='disabled')
            self.run_button.config(state='disabled')


        else:

            self.token = f'Bearer {self.token}'

            self.username = self.username_input.get()
            self.password = self.password_input.get()
            self.login_verified = True

            print(self.auto_state.get(), self.remember_state.get())

            record_username = self.username
            record_password = self.password if self.remember_state.get() else 'N/A'
            record_auto_login = '1' if self.auto_state.get() else '0'

            self.user_list.add_user(user_info.User(record_username, record_password, record_auto_login, time.time()))
            self.user_list.write_user_list()
            self.get_first_name()

            self.title(f'百工汇智PDM拓展程序————{self.first_name}')
            self.select_folder_button.config(state='normal')
            if self.folder_textbox.get():
                self.run_button.config(state='normal')

            self.refresh_history_upload()

            messagebox.showinfo(title='登录成功', message='登录成功\n欢迎您，'+self.first_name)

            self.login_window.destroy()


    def on_click_refresh_button(self):
        if not self.login_verified:
            messagebox.showerror(title='未登录', message='请登录后再查看历史记录')
            return

        messagebox.showinfo(title='已刷新', message='已刷新零部件上传历史记录')

        self.refresh_history_upload()


    def refresh_history_upload(self):

        self.tree.delete(*self.tree.get_children())

        self.part_list = download_file.get_part(self.id, self.token)
        print('test', self.part_list)

        # with open('upload_history.txt', 'r') as file:
        #     lines = file.readlines()
        #     for line in lines:
        #         print(line)
        #         temp = (file_name, file_id, file_date, file_time) = line.split(sep='&&')
        #         temp[3] = temp[3][:-1]
        #         self.part_list.append(temp)
        #     print(self.part_list)

        tree_data = [
            *[("", x, self.part_list[x - 1][0], (self.part_list[x - 1][4], self.part_list[x - 1][2], self.part_list[x - 1][3])) for x in range(1, len(self.part_list) + 1)],
        ]


        for item in tree_data:
            print(item)
            parent, iid, item_number, value = item
            # print(parent, item_number, name, modified_time, code, item)
            self.tree.insert(parent=parent, index="end", iid=iid, text=item_number, values=value)

    def get_first_name(self):
        url = 'http://47.96.66.12/InnovatorServer/Server/odata/User'
        headers = {'Authorization': self.token}

        r = requests.get(url, headers=headers)
        for user in r.json()['value']:
            if user['login_name'] == self.username:
                self.id = user['id']
                self.first_name = user['first_name']
                print(self.id, self.first_name, self.token)
                return
        self.first_name = None

    def login(self):
        # login_thread = threading.Thread(target=self.login_thread_job)
        if len(threading.enumerate()) == 1:
            self.token = generate_token.generate(self.username_input.get(), self.password_input.get())
            if self.token is None:
                messagebox.showerror(title='登录失败', message='用户名或密码错误')
                self.login_verified = False
            else:
                messagebox.showinfo(title='登录成功', message='登录成功')

                self.token = f'Bearer {self.token}'

                self.username = self.username_input.get()
                self.password = self.password_input.get()
                self.login_verified = True

    def select_folder(self):
        """选择文件夹的地址"""

        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_textbox.config(state=tk.NORMAL)
            self.folder_textbox.delete(0, tk.END)
            self.folder_textbox.insert(0, folder_selected)
            self.run_button.config(state='normal')

    def clear_folder(self):
        """清空页面"""

        self.folder_textbox.config(state=tk.NORMAL)
        self.folder_textbox.delete(0, tk.END)
        self.folder_textbox.config(state='readonly')
        self.progress.set('进度: 未开始上传\n')
        self.progress_bar['value'] = 0
        self.file_progress.set('0/0')
        self.output_textbox.delete(1.0, tk.END)

    def add_line(self, line):
        """在文本框内加入新的一行"""

        self.output_textbox.insert('end', line + '\n')

    def cad_thread_job(self, part, cad):
        """上传输入的工程图，并将上传结果输出在文本框之中"""

        try:
            part.upload_cad(cad, self.username, self.overwrite, self.token)
        except UploadFinish as e:
            self.add_line(str(e))
        except EmptyFileError as e:
            self.add_line(str(e))
        except InsufficientPermissionsError as e:
            self.add_line(str(e))
        except SkipExist as e:
            self.add_line(str(e))

    def doc_thread_job(self, part, doc):
        """上传输入的文档，并将上传结果输出在文本框之中"""

        try:
            part.upload_document(doc, self.username, self.overwrite, self.token)
        except UploadFinish as e:
            self.add_line(str(e))
        except EmptyFileError as e:
            self.add_line(str(e))
        except InsufficientPermissionsError as e:
            self.add_line(str(e))
        except SkipExist as e:
            self.add_line(str(e))

    def upload_thread_job(self):
        """上传读取的目录结构"""

        self.running = True

        # 获取零部件的总数，记录已上传的零部件和文件数量，以供进度条使用
        total_parts = len(self.b.get_parts())
        part_counter = 0
        file_counter = 0

        # 根据排好的顺序，遍历零部件
        for part in self.b.get_parts():
            # 更新进度条显示
            part_counter += 1
            progress_header = f'进度: 正在上传第{part_counter}/{total_parts}个零部件'
            self.progress.set(progress_header)

            # 上传该零部件的附属工程图
            # total_cad = len(part.get_cad())
            # cad_counter = 0
            for cad in part.get_cad():
                if not self.running:
                    self.progress.set('进度: 上传已终止')
                    self.add_line('上传已终止')
                    messagebox.showinfo(title='终止', message='上传已终止')
                    return
                # cad_counter += 1
                # self.progress.set(progress_header + f'工程图: {cad_counter}/{total_cad}')
                cad_thread = threading.Thread(target=self.cad_thread_job, args=(part, cad))
                cad_thread.start()
                cad_thread.join()
                file_counter += 1
                self.file_progress.set(f'{file_counter}/{self.total_files}')
                self.progress_bar['value'] = file_counter / self.total_files * 100

            # 上传该零部件的附属文档
            # total_doc = len(part.get_document())
            # doc_counter = 0
            for doc in part.get_document():
                if not self.running:
                    self.progress.set('进度: 上传已终止')
                    self.add_line('上传已终止')
                    messagebox.showinfo(title='终止', message='上传已终止')
                    return
                # doc_counter += 1
                # self.progress.set(progress_header + f'文档: {doc_counter}/{total_doc}')
                doc_thread = threading.Thread(target=self.doc_thread_job, args=(part, doc))
                doc_thread.start()
                doc_thread.join()
                file_counter += 1
                self.file_progress.set(f'{file_counter}/{self.total_files}')
                self.progress_bar['value'] = file_counter / self.total_files * 100

            # 添加该零部件的子零部件属性
            if not self.running:
                self.progress.set('进度: 上传已终止')
                self.add_line('上传已终止')
                messagebox.showinfo(title='终止', message='上传已终止')
                return
            part.add_subpart_relation(self.token)

            # 上传该零部件
            if not self.running:
                self.progress.set('进度: 上传已终止')
                self.add_line('上传已终止')
                messagebox.showinfo(title='终止', message='上传已终止')
                return
            try:
                part.upload_part(self.token)
            except UploadFinish as e:
                self.add_line(str(e) + '\n')
            except InsufficientPermissionsError as e:
                self.add_line(str(e) + '\n')

        self.add_line('目录结构上传结束')
        self.progress.set('进度: 上传结束')
        messagebox.showinfo(title='上传结束', message='目录结构上传结束')

    def run_function(self):
        """处理点击后的各种验证，然后开始上传目录结构"""

        self.output_textbox.delete(1.0, tk.END)

        self.select_folder_button.config(state=tk.DISABLED)
        self.run_button.config(state=tk.DISABLED)

        # 验证登录 --------------------------------------
        if self.login_verified:
            pass
        else:
            messagebox.showerror(title='未登录', message='请登录后再进行上传')
            self.select_folder_button.config(state=tk.NORMAL)
            self.run_button.config(state=tk.NORMAL)
            return

        # 验证是否选择文件夹 ----------------------------------
        selected_folder = self.folder_textbox.get()
        if selected_folder:
            pass
        else:
            messagebox.showerror(title='错误', message='未选择文件夹')
            self.select_folder_button.config(state=tk.NORMAL)
            self.run_button.config(state=tk.NORMAL)
            return

        # 验证文件夹名称格式 --------------------------------
        name = selected_folder.split('/')[-1]
        position = name.find('.')
        if position != -1 and name[position + 1].find('.') == -1:
            pass
        else:
            messagebox.showerror(title='错误', message='选择的文件夹名称格式有误')
            self.select_folder_button.config(state=tk.NORMAL)
            self.run_button.config(state=tk.NORMAL)
            return

        # 读取文件夹 --------------------------------------
        self.b = bom.BOM(selected_folder, self.token)
        self.total_files = 0
        for part in self.b.get_parts():
            self.total_files += len(part.get_document())
            self.total_files += len(part.get_cad())
        self.file_progress.set(f'0/{self.total_files}')

        # 查询存在+覆盖与否 ----------------------------------------
        root = self.b._root
        r = search.exist_part(root.get_name(), root.get_code(), self.token)
        if r:
            self.overwrite = messagebox.askyesno(title='零部件已存在',
                                                 message=f'{root.get_name()}已存在，'
                                                         f'是否覆盖该零部件以及其下属零部件？')

        # 上传 ------------------------------------------------------
        upload_thread = threading.Thread(target=self.upload_thread_job)
        upload_thread.start()

        self.select_folder_button.config(state=tk.NORMAL)
        self.run_button.config(state=tk.NORMAL)


if __name__ == '__main__':
    gui = BeautifulGUI()
    gui.mainloop()
