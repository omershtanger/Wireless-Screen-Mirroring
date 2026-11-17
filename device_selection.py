import sys
import threading
import time
import tkinter
import tkinter.messagebox
import customtkinter
from tkinter import ttk
import encrypted_socket
from stream import Stream


class App(customtkinter.CTk):
    def __init__(self, session_id):
        super().__init__()

        self.session_id = session_id
        self.sock = encrypted_socket.EncryptedSocket()
        err = self.sock.connect()
        if err:
            tkinter.messagebox.showerror(
                "Error", "Failed to connect to server")
            self.destroy()
            sys.exit(1)

        # configure window
        self.title("Mirroring screen")
        self.geometry(f"{400}x{300}")
        self.columnconfigure((0, 1, 2), weight=1)
        self.configure(fg_color="gray15")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.DevicesLabel = customtkinter.CTkLabel(
            self, text="Devices", font=("San Francisco", 26, "bold"))
        self.DevicesLabel.grid(row=0, column=1, pady=30, columnspan=1)

        style = ttk.Style()
        style.configure("CustomSeparator.TSeparator", background="#000")

        # create scrollable frame
        self.scrollable_frame = customtkinter.CTkScrollableFrame(
            self, fg_color="gray9", scrollbar_button_color="gray9", scrollbar_button_hover_color="gray9", corner_radius=0)
        self.scrollable_frame.grid(
            row=2, columnspan=4, padx=0, pady=0, sticky="ew")

        self.separator1 = ttk.Separator(
            self, style="CustomSeparator.TSeparator")
        self.separator1.grid(row=1, columnspan=4, pady=0, sticky="ew")

        # {name: True/False}
        # True if activated
        self.devices = {}
        t = threading.Thread(target=self.update_devices)
        t.start()

        stream = Stream(self.session_id)
        stream.stream_video()

    def update_devices(self):
        request = {
            "type": "get devices",
            "session_id": self.session_id
        }
        while True:
            try:
                self.sock.send_data(request)
                response = self.sock.receive_response()

                # Create a list to track the devices in the response
                response_devices = response['devices']

                # Keep track of separators
                separators_to_remove = []

                # Check if at least one device button exists
                device_button_exists = False

                # Iterate over existing device buttons and separators
                for widget in self.scrollable_frame.winfo_children():
                    if isinstance(widget, customtkinter.CTkButton):
                        device = widget.cget("text")
                        if device not in response_devices:
                            # Remove the device button from the scrollable frame
                            widget.pack_forget()
                            widget.destroy()
                            del self.devices[device]
                            device_button_exists = True
                            # Find the corresponding separator and add it to the list for removal
                            for separator in separators_to_remove:
                                if separator.master == self.scrollable_frame:
                                    separators_to_remove.remove(separator)
                                    break
                    elif isinstance(widget, ttk.Separator):
                        if device_button_exists and widget not in separators_to_remove:
                            separators_to_remove.append(widget)

                # Remove the separators marked for removal
                for separator in separators_to_remove:
                    separator.pack_forget()
                    separator.destroy()

                for device in response_devices:
                    if device not in self.devices:
                        self.devices[device] = False
                        device_button = customtkinter.CTkButton(master=self.scrollable_frame, fg_color="transparent",
                                                                hover_color="gray20", text_color="#FFCCCC",
                                                                text=f"{device}", corner_radius=0, height=50, width=500,
                                                                anchor="w", font=("San Francisco", 16))
                        device_button.pack()
                        separator = ttk.Separator(
                            self.scrollable_frame, style="CustomSeparator.TSeparator")
                        separator.pack(fill=tkinter.BOTH, expand=True)

                        # Bind the toggle_device method to the button
                        device_button.configure(
                            command=lambda button=device_button, device=device: self.toggle_device(button, device))
                time.sleep(3)

            except Exception as e:
                break

    def toggle_device(self, button, device):
        if self.devices[device]:
            self.devices[device] = False
            button.configure(text_color="#FFCCCC")
        else:
            self.devices[device] = True
            button.configure(text_color="#CCFFCC")

        request = {
            "type": "toggle device",
            "session_id": self.session_id,
            "device name": device,
            "active": self.devices[device]
        }

        self.sock.send_data(request)

    def on_closing(self):
        print('closing')
        request = {
            "type": "logout",
            "session_id": self.session_id,
        }
        self.sock.send_data(request)
        self.sock.close()
        self.destroy()
        sys.exit(0)
