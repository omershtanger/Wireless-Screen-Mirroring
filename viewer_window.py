import base64
import threading
import tkinter as tk
from PIL import Image, ImageTk
import socket
import io
import tkinter
import tkinter.messagebox
import customtkinter
from tkinter import Tk, ttk
import wmi
import encrypted_socket
import soundcard as sc
import numpy as np
import subprocess
import psutil
import pyautogui

# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self, session_id):
        super().__init__()
        self.session_id = session_id
        self.sock = encrypted_socket.EncryptedSocket()
        self.sock.connect()
        self.started=False
        self.open=True
        self.viewer_open=False
        self.screen_width, self.screen_height = pyautogui.size()


        # configure window
        self.title("")
        self.geometry(f"{900}x{530}")
        self.configure(fg_color="gray6")
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # configure grid layout (4x4)
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0), weight=1)

        # create radiobutton frame
        self.mainframe = customtkinter.CTkFrame(
            self, corner_radius=12, fg_color="gray11")
        self.mainframe.grid(row=0, column=0, padx=(
            30, 12), pady=30, sticky="nsew")
        self.mainframe.rowconfigure((0, 1, 2, 3), weight=1)
        self.mainframe.columnconfigure((0, 1, 2), weight=1)

        self.infoframe = customtkinter.CTkFrame(
            self, corner_radius=12, fg_color="gray11")
        self.infoframe.grid(row=0, column=1, padx=(
            12, 30), pady=30, sticky="nsew")

        self.infoframe.grid_columnconfigure((0), weight=1)
        self.infoframe.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        self.settings = customtkinter.CTkLabel(
            self.infoframe, text="Settings", font=("San Francisco", 30, "bold"))
        self.settings.grid(row=0, column=0, padx=20, pady=20, sticky="sew")

        self.group1 = customtkinter.CTkFrame(
            self.infoframe, corner_radius=15, height=140, fg_color="gray14")
        self.group1.grid(row=1, column=0, padx=20, pady=20, sticky="new")

        self.group1.grid_columnconfigure((0), weight=1)
        self.group1.grid_rowconfigure((0, 1, 2), weight=1)

        style = ttk.Style()
        style.configure("CustomSeparator.TSeparator", background="#000")

        self.separator = ttk.Separator(
            self.group1, style="CustomSeparator.TSeparator")
        self.separator.grid(row=1, column=0, columnspan=2,
                            padx=20, pady=10, sticky="ew")

        self.networklabel = customtkinter.CTkLabel(
            master=self.group1, text=" Network", font=("San Francisco", 14, "bold"))
        self.networklabel.grid(
            row=0, column=0, columnspan=1, padx=10, pady=10, sticky="w")

        self.conn = customtkinter.CTkLabel(master=self.group1, text_color=(
            "gray65"), text=self.get_wifi_name(), font=("San Francisco", 14))
        self.conn.grid(row=0, column=1, columnspan=1,
                       padx=10, pady=10, sticky="e")

        self.namelabel = customtkinter.CTkLabel(
            master=self.group1, text=" Device", font=("San Francisco", 14, "bold"))
        self.namelabel.grid(row=2, column=0, columnspan=1,
                            padx=10, pady=10, sticky="w")

        self.device = customtkinter.CTkLabel(master=self.group1, text_color=(
            "gray65"), text=self.get_device_name(), font=("San Francisco", 14))
        self.device.grid(row=2, column=1, columnspan=1,
                         padx=10, pady=10, sticky="e")

        self.mode = customtkinter.CTkFrame(
            self.infoframe, corner_radius=15, fg_color="gray14")
        self.mode.grid_columnconfigure((0, 1, 2), weight=1)
        self.mode.grid_rowconfigure((0, 1, 2, 3, 4, 5),  weight=1)
        self.mode.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

        self.separator1 = ttk.Separator(
            self.mode, style="CustomSeparator.TSeparator")
        self.separator1.grid(row=1, column=0, columnspan=6,
                             padx=20, pady=10, sticky="ew")
        self.separator2 = ttk.Separator(
            self.mode, style="CustomSeparator.TSeparator")
        self.separator2.grid(row=3, column=0, columnspan=6,
                             padx=20, pady=5, sticky="ew")

        self.Displaylabel = customtkinter.CTkLabel(
            master=self.mode, text="Display Mode", font=("San Francisco", 18, "bold"))
        self.Displaylabel.grid(
            row=0, column=0, columnspan=2, pady=(15, 10), sticky='e')

        self.switch_var = tkinter.IntVar(value=0)
        self.Minilabel = customtkinter.CTkLabel(
            master=self.mode, text="  Mini Player", font=("San Francisco", 16))
        self.Minilabel.grid(row=2, column=0, columnspan=1,
                            padx=5, pady=5, sticky="w")
        self.MiniPlayer = customtkinter.CTkSwitch(master=self.mode, variable=self.switch_var, onvalue=0, offvalue=1,
                                                  border_width=0, width=10, switch_height=22, switch_width=40, progress_color="medium sea green", text="", command=self.on_switch_change)
        self.MiniPlayer.grid(row=2, column=3, columnspan=3,
                             padx=10, pady=5, sticky="e")

        self.Fulllabel = customtkinter.CTkLabel(
            master=self.mode, text="  Full Screen", font=("San Francisco", 16))
        self.Fulllabel.grid(row=4, column=0, columnspan=1,
                            padx=5, pady=5, sticky="w")
        self.FullScreen = customtkinter.CTkSwitch(master=self.mode, variable=self.switch_var, onvalue=1, offvalue=0,
                                                  border_width=0, width=10, switch_height=22, switch_width=40, progress_color="medium sea green", text="", command=self.on_switch_change)
        self.FullScreen.grid(row=4, column=3, columnspan=3,
                             padx=10, pady=5, sticky="e")

        self.ViewAirLabel = customtkinter.CTkLabel(
            master=self.mainframe, text="ViewAir", font=("San Francisco", 40, "bold"))
        self.ViewAirLabel.grid(row=1, column=1, columnspan=1,
                               padx=20, pady=20, sticky="ew")

        self.Moreinfolabel = customtkinter.CTkLabel(
            master=self.mainframe, text="Wirelessly share content from your device", font=("San Francisco", 20))
        self.Moreinfolabel.grid(
            row=2, column=1, columnspan=1, padx=0, pady=20, sticky="ew")

        self.Warnning = customtkinter.CTkLabel(
            master=self.mainframe, text="Make sure your device is connected to the same network", text_color=("gray65"), font=("San Francisco", 12))
        self.Warnning.grid(row=3, column=1, columnspan=1,
                           padx=0, pady=20, sticky="ew")

        self.open_viewer_window()
        self.screenshots_socket = encrypted_socket.EncryptedSocket()
        self.screenshots_socket.connect()

        screenshots_request = {
            "type": "register viewer",
            "socket type": "screenshots",
            "session_id": self.session_id,
            "device name": socket.gethostname()
        }

        self.screenshots_socket.send_data(screenshots_request)

        screenshots_thread = threading.Thread(target=self.receive_screenshots)
        screenshots_thread.start()

    def on_switch_change(self):
        if self.switch_var.get() == 1:
            self.view_window.geometry(f"{self.screen_width}x{self.screen_height}")
            self.view_window.wm_attributes('-topmost', 0)
            self.view_window.attributes('-fullscreen', True)
            self.canvas.configure(width=self.view_window.winfo_screenwidth(), height=self.view_window.winfo_screenheight())

        else:
            self.view_window.attributes('-fullscreen', False)
            self.view_window.geometry("700x350")
            self.view_window.wm_attributes('-topmost', 1)
            self.canvas.configure(width=700, height=350)

    def get_wifi_name(self):
        try:
            raw_output = subprocess.check_output(['netsh', 'WLAN', 'show', 'interfaces'])
            output_lines = raw_output.decode('utf-8').splitlines()

            for line in output_lines:
                if 'SSID' in line:
                    return line.split(':')[1].strip()

        except subprocess.CalledProcessError:
            pass
        return self.get_ethernet_name(self)

    def get_ethernet_name(self):
        interfaces = psutil.net_if_stats()

        for interface, stats in interfaces.items():
            if stats.isup and not interface.startswith('lo'):
                return interface
        
        return "No Connection"


    def get_device_name(self):
        return socket.gethostname()
    
    
    def open_viewer_window(self):
        self.view_window = tk.Toplevel(self)
        self.view_window.configure(bg="black")
        self.view_window.wm_attributes('-topmost', 1)
        self.view_window.title('Viewer window')
        self.view_window.geometry("700x350")
        self.view_window.geometry("+0+0")
        self.view_window.wm_resizable(1, 1)
        self.view_window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.canvas = tk.Canvas(self.view_window, width=700, height=350, bg="black")
        self.canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.photo_image = None
        self.view_window.withdraw()

    def receive_screenshots(self):
        while True:
            try:
                info = self.screenshots_socket.receive_response()
                if 'type' in info:
                    if info["type"] == "screenshot":
                        screenshot = info["screenshot"]
                        image_data = base64.b64decode(screenshot)
                        self.screenshot = Image.open(io.BytesIO(image_data))
                        width, height = self.view_window.winfo_width(), self.view_window.winfo_height()
                        self.screenshot.thumbnail((width, height))
                        self.photo_image = ImageTk.PhotoImage(self.screenshot)
                        self.canvas.create_image(
                            width/2, height/2, anchor='center', image=self.photo_image)
                        self.canvas.configure(width=width,height=height)
                        self.canvas.photo_image=self.photo_image
                    elif info['type']=='start':
                        self.view_window.deiconify()
                        self.viewer_open=True
                    elif info['type']=='stop':
                        self.view_window.withdraw()
                        self.viewer_open=False
                    elif info['type'] == 'logout':
                        self.view_window.withdraw()
                        self.viewer_open=False
                        tkinter.messagebox.showinfo('','Waiting for a new streamer')
            except Exception as e:
                break
        print('done')
    
    def on_close(self):
        self.screenshots_socket.close()
        self.view_window.destroy()
        self.destroy()

   


