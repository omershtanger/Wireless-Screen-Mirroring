import sys
import tkinter as tk
import tkinter.messagebox
import customtkinter
from tkinter import ttk
import encrypted_socket


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.sock = encrypted_socket.EncryptedSocket()
        err = self.sock.connect()
        if err:
            self.destroy()
            sys.exit(1)

        # configure window
        self.title("")
        self.configure(fg_color="gray7")
        self.geometry(f"{450}x{500}")
        self.resizable(False, False)

        def on_close():
            import login_window
            self.destroy()
            login_window.App().mainloop()
        self.protocol("WM_DELETE_WINDOW", on_close)


        # configure grid layout (4x4)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(
            (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14), weight=1)

        self.Header = customtkinter.CTkLabel(
            master=self, text="New Account", font=("San Francisco", 30, "bold"))
        self.Header.grid(row=2, column=0, columnspan=2,
                         padx=20, pady=20, sticky="ew")
        style = ttk.Style()
        # Set the desired gray color
        style.configure("CustomSeparator.TSeparator", background="#000")

        self.usernameframe = customtkinter.CTkFrame(
            self, corner_radius=12, fg_color="gray11")
        self.usernameframe.grid(
            row=4, column=0, columnspan=2, padx=20, pady=0, sticky="ew")
        self.usernameframe.columnconfigure((0, 1, 2), weight=1)
        self.usernameframe.rowconfigure((0), weight=1)

        self.passwordframe = customtkinter.CTkFrame(
            self, corner_radius=12, fg_color="gray11")
        self.passwordframe.grid(
            row=6, column=0, columnspan=2, padx=20, pady=0, sticky="ew")
        self.passwordframe.columnconfigure((0, 1, 2), weight=1)
        self.passwordframe.rowconfigure((0, 1, 2), weight=1)

        self.usernamelabel = customtkinter.CTkLabel(
            master=self.usernameframe, text="Username", font=("San Francisco", 14, "bold"))
        self.usernamelabel.grid(row=0, column=0, padx=20, pady=5, sticky="w")

        self.passwordlabel = customtkinter.CTkLabel(
            master=self.passwordframe, text="Password", font=("San Francisco", 14, "bold"))
        self.passwordlabel.grid(row=0, column=0, padx=20, pady=5, sticky="w")

        self.verifylabel = customtkinter.CTkLabel(
            master=self.passwordframe, text="Verify", font=("San Francisco", 14, "bold"))
        self.verifylabel.grid(row=2, column=0, padx=20, pady=5, sticky="w")

        self.username = customtkinter.CTkEntry(master=self.usernameframe, border_width=0, fg_color=self.usernameframe.cget(
            "fg_color"), placeholder_text="Required", font=("San Francisco", 14))
        self.username.grid(row=0, column=1, columnspan=2,
                           padx=20, pady=5, sticky="w")

        self.separator1 = ttk.Separator(
            self.passwordframe, style="CustomSeparator.TSeparator")
        self.separator1.grid(row=1, column=0, columnspan=4,
                             padx=10, pady=5, sticky="ew")

        self.password = customtkinter.CTkEntry(master=self.passwordframe, border_width=0, fg_color=self.passwordframe.cget(
            "fg_color"), placeholder_text="Required", show='\u25cf', font=("San Francisco", 14))
        self.password.grid(row=0, column=1, columnspan=2,
                           padx=20, pady=5, sticky="w")

        self.verify_password = customtkinter.CTkEntry(master=self.passwordframe, border_width=0, fg_color=self.passwordframe.cget(
            "fg_color"), placeholder_text="Required", show='\u25cf', font=("San Francisco", 14))
        self.verify_password.grid(
            row=2, column=1, columnspan=2, padx=20, pady=5, sticky="w")

        self.register = customtkinter.CTkButton(master=self, text="Continue", font=(
            "San Francisco", 17), fg_color="dodger blue2", command=self.on_register_clicked, height=37, width=110, corner_radius=10)
        self.register.grid(row=11, column=0, columnspan=1,
                           padx=20, pady=0, sticky="e")

        self.requirments1 = customtkinter.CTkLabel(
            master=self, text="Your password must be at least 8 characters, include a number, a sign, ", text_color="gray65", font=("San Francisco", 12))
        self.requirments1.grid(row=7, columnspan=2,
                               pady=0, padx=30, sticky="sw")

        self.requirments2 = customtkinter.CTkLabel(
            master=self, text="an uppercase letter, and a lowercase letter.", text_color="gray65", font=("San Francisco", 12))
        self.requirments2.grid(row=8, columnspan=2,
                               pady=0, padx=30, sticky="nw")

        self.username_requirments = customtkinter.CTkLabel(
            master=self, text="Your username must be at least 6 characters", text_color="gray65", font=("San Francisco", 12))
        self.username_requirments.grid(
            row=5, columnspan=2, padx=30, sticky="nw")

    def on_register_clicked(self):
        username = self.username.get()
        password = self.password.get()
        password2 = self.verify_password.get()

        if password != password2:
            tkinter.messagebox.showerror("Error", "Passwords do not match")
            return

        request = {
            "type": "register",
            "username": username,
            "password": password
        }

        self.sock.send_data(request)
        response = self.sock.receive_response()

        try:
            if response["success"]:
                print("Register successful")
                import login_window
                self.destroy()
                login_window.App().mainloop()
            else:
                tkinter.messagebox.showerror("Failed to register", response["msg"])
        except Exception as e:
            print("unavailable server")
