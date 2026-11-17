import json
import socket
import ssl
import tkinter.messagebox
import constants
import tkinter as tk
class EncryptedSocket:
    def __init__(self):
        self.error_shown=False
        root = tk.Tk()
        root.withdraw()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            self.enc_socket = context.wrap_socket(
                sock, server_hostname=constants.SERVER_IP)
        except socket.error as e:
            if e.errno!=10053 and e.errno!=10038:
                if not self.error_shown:
                    tkinter.messagebox.showerror('Error', 'Server is unavailable')
                    self.error_shown=True

    def connect(self):
        try:
            self.enc_socket.connect(
                (constants.SERVER_IP, constants.SERVER_PORT))
        except socket.error as e:
            if e.errno==10053 or e.errno==10038:
                return None
            else:
                if not self.error_shown:
                    tkinter.messagebox.showerror('Error', 'Server is unavailable')
                    self.error_shown=True
                return True

    def send_data(self, request: dict):
        try:
            request_json = json.dumps(request).encode()
            request_length = len(request_json).to_bytes(4, byteorder='big')
            self.enc_socket.sendall(request_length + request_json)
        except socket.error as e:
            if e.errno==10053 or e.errno==10038:
                return None
            else:
                if not self.error_shown:
                    tkinter.messagebox.showerror('Error', 'Server is unavailable')
                    self.error_shown=True


    def receive_response(self) -> dict:
        try:
            response_length_bytes = self.enc_socket.recv(4)
            response_length = int.from_bytes(
                response_length_bytes, byteorder='big')
            received_data = b""
            while len(received_data) < response_length:
                chunk = self.enc_socket.recv(response_length - len(received_data))
                received_data += chunk
            if not received_data:
                if not self.error_shown:
                    tkinter.messagebox.showerror('Error', 'Server is unavailable')
                    self.error_shown=True
            response_json = received_data.decode()
            return json.loads(response_json)
        except socket.error as e:
            if e.errno==10053 or e.errno==10038:
                return None
            elif "SSL: TLSV1_ALERT_INTERNAL_ERROR" in str(e):
                tkinter.messagebox.showerror('Error', 'Please try to login again')
            else:
                if not self.error_shown:
                    tkinter.messagebox.showerror('Error', 'Server is unavailable')
                    self.error_shown=True


    def close(self):
        try:
            self.enc_socket.close()
        except socket.error as e:
            if e.errno==10053 or e.errno==10038:
                return None
            else:
                if not self.error_shown:
                    tkinter.messagebox.showerror('Error', 'Server is unavailable')
                    self.error_shown=True

