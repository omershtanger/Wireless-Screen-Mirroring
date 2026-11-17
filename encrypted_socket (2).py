import json
import socket
import ssl
import tkinter.messagebox
import tkinter as tk
import constants


class EncryptedSocket:
    def __init__(self):
        root = tk.Tk()
        root.withdraw()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((constants.SERVER_IP, constants.SERVER_PORT))
            sock.listen()
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(
                certfile=constants.SERVER_CERT, keyfile=constants.SERVER_KEY)
            self.enc_socket = context.wrap_socket(sock, server_side=True)
            print("Server started and listening for connections...")
        except Exception as e:
            tkinter.messagebox.showerror('Error', 'Server is unavailable')

    def accept(self):
        try:
            return self.enc_socket.accept()
        except Exception as e:
            pass

    def send_reply(self, client_socket: socket.socket, reply: dict):
        try:
            reply_json = json.dumps(reply).encode()
            reply_length = len(reply_json).to_bytes(4, byteorder='big')
            client_socket.sendall(reply_length + reply_json)
        except Exception as e:
            pass

    def get_client_request(self, client_socket: socket.socket):
        try:
            request_length_bytes = client_socket.recv(4)
            if not request_length_bytes:
                return None

            request_length = int.from_bytes(request_length_bytes, byteorder='big')
            data = b""
            remaining_bytes = request_length
            while remaining_bytes > 0:
                chunk = client_socket.recv(min(4096, remaining_bytes))
                if not chunk:
                    break
                data += chunk
                remaining_bytes -= len(chunk)

            if len(data) < request_length:
                return None

            return json.loads(data.decode())
        except Exception as e:
            pass

    def close(self):
        try:
            self.enc_socket.close()
        except Exception as e:
            pass
