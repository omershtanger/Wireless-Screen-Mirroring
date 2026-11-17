import socket
import sys
import tkinter as tk
import tkinter.messagebox
import customtkinter
from tkinter import ttk
import device_selection
import viewer_window
import encrypted_socket

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"    


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
        self.configure(fg_color="gray6")
        self.geometry(f"{450}x{500}")
        self.resizable(False,False)

        # configure grid layout (4x4)
        self.grid_columnconfigure((0,1), weight=1)
        self.grid_rowconfigure((0,1,2,3,4,5,6,7,8,9,10,11,12,13,14), weight=1)

        self.Header=customtkinter.CTkLabel(master=self, text="ViewAir", font=("San Francisco", 30, "bold"))
        self.Header.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        style = ttk.Style()
        style.configure("CustomSeparator.TSeparator", background="#000")  # Set the desired gray color

        self.loginframe = customtkinter.CTkFrame(self, corner_radius=12, fg_color="transparent")
        self.loginframe.grid(row=5, column=0, columnspan=2, padx=20, pady=0, sticky="ew")
        self.loginframe.columnconfigure((0,1), weight=1)
        self.loginframe.rowconfigure((0,1,2,3,4), weight=1)

        self.usernamelabel=customtkinter.CTkLabel(master=self.loginframe, text="Username", font=("San Francisco", 14, "bold"))
        self.usernamelabel.grid(row=1, column=0, padx=20, pady=7, sticky="w")
        
        self.passwordlabel=customtkinter.CTkLabel(master=self.loginframe, text="Password", font=("San Francisco", 14, "bold"))
        self.passwordlabel.grid(row=3, column=0, padx=20, pady=7, sticky="w")

        self.username = customtkinter.CTkEntry(master=self.loginframe, border_width=0 ,fg_color=self.loginframe.cget("fg_color"),placeholder_text="Required", font=("San Francisco", 14))
        self.username.grid(row=1, column=1, columnspan=2, padx=20, pady=7, sticky="w")

        self.separator1 = ttk.Separator(self.loginframe, style="CustomSeparator.TSeparator")
        self.separator1.grid(row=0, column=0, columnspan=4, padx=5, pady=7, sticky="ew")

        self.separator2 = ttk.Separator(self.loginframe, style="CustomSeparator.TSeparator")
        self.separator2.grid(row=2, column=0, columnspan=4, padx=5, pady=7, sticky="ew")

        self.separator3 = ttk.Separator(self.loginframe, style="CustomSeparator.TSeparator")
        self.separator3.grid(row=4, column=0, columnspan=4, padx=5, pady=7, sticky="ew")

        self.password = customtkinter.CTkEntry(master=self.loginframe, border_width=0 ,fg_color=self.loginframe.cget("fg_color"), placeholder_text="Required", font=("San Francisco", 14), show='\u25cf')
        self.password.grid(row=3, column=1, columnspan=2, padx=20, pady=7, sticky="w")

        self.mode_var=tkinter.StringVar(value="Mirror")
        self.mode = customtkinter.CTkSegmentedButton(self, values=["Mirror", "View"], dynamic_resizing=False, fg_color="gray12", unselected_color="gray16", border_width=2, selected_hover_color="dodger blue2", unselected_hover_color="dodger blue2", font=("San Francisco", 13),variable=self.mode_var)
        self.mode.grid(row=7, column=0, padx=(20, 10), pady=0, sticky="w")

        register = customtkinter.CTkButton(master=self, text="Don't have an account?", font=("San Francisco", 14), fg_color="transparent", text_color="dodger blue2",text_color_disabled="gray30", command=self.switch_to_register, hover_color="gray6")
        register.grid(row=11, column=0, columnspan=2, padx=20, pady=0)

        login = customtkinter.CTkButton(master=self, text="Continue", font=("San Francisco", 17), fg_color="dodger blue2", command=self.on_login_clicked, height=37, width=110, corner_radius=10)
        login.grid(row=10, column=0, columnspan=2, padx=20, pady=0)

    def switch_to_register(self):
        self.destroy()
        import register_window
        w = register_window.App()
        w.mainloop()    

    def on_login_clicked(self):
        username = self.username.get()
        user_type = self.mode_var.get()
        password = self.password.get()

        request = {
            "type": "login",
            "username": username,
            "user_type": user_type,
            "password": password,
            "device name": socket.gethostname()
        }

        self.sock.send_data(request)
        response = self.sock.receive_response()
        try:
            if response["success"]:
                print("Login successful")
                self.destroy()
                if user_type == "Mirror":
                    device_selection.App(response['session_id']).mainloop()                
                else:
                    viewer_window.App(response['session_id']).mainloop()                
                
            else:
                tkinter.messagebox.showerror("Error", response['err'])
        except Exception as e:
            print("unavailable server")