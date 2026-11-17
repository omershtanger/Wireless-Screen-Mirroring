import socket
import threading
import uuid
import db
import encrypted_socket


class Server:
    def __init__(self):
        db.create_tables()
        self.enc_socket = encrypted_socket.EncryptedSocket()

        # {session_id: username}
        self.sessions = {}

        # {username: {pc_name: {sockets: [video_socket], active: True/False}}}
        self.streamers = {}

        # {username: True/False}
        self.steamer_active = {}

    def accept_connections(self):
        while True:
            try:
                client_socket, address = self.enc_socket.accept()
                client_thread = threading.Thread(
                    target=self.handle_client, args=(client_socket, address))
                client_thread.start()
            except Exception as e:
                pass

    def handle_client(self, client_socket: socket.socket, address):
        print(f"Client connected from {address}")
        while True:
            try:
                request = self.enc_socket.get_client_request(client_socket)
                if request is None:
                    break
                action = request['type']
                if action == 'login':
                    self.handle_login(request, client_socket)
                elif action == 'logout':                                    
                    self.handle_logout(request)
                elif action == 'register':
                    self.handle_register(request, client_socket)
                elif action == 'get devices':
                    self.handle_get_devices(request, client_socket)
                elif action == 'register viewer':
                    self.handle_register_viewer(request, client_socket)
                elif action == 'toggle device':
                    self.handle_toggle_device(request)
                elif action == 'client screenshot':
                    self.handle_client_screenshot(request, client_socket)
            except:
                break

        self.remove_pc_name_by_socket(client_socket)
        client_socket.close()
        print(f"Client disconnected from {address}")

    def handle_login(self, request: dict, client_socket: socket.socket):
        username = request['username']
        response = {}
        if db.login_user(username, request['password']) == "false":
            response = {"success": False, "err": "Invalid username or password"}
        elif db.login_user(username, request['password']) == "success":
            if request['user_type'] == 'Mirror':
                if username in self.streamers:
                    if self.steamer_active[username]:
                        response = {"success": False,
                                    "err": "Already mirroring from this account"}
                    else:
                        self.steamer_active[username] = True
                else:
                    self.streamers[username] = {}
                    self.steamer_active[username] = True

            else:
                if username not in self.streamers:
                    response = {"success": False,
                                "err": "First mirror from this account"}
                elif request['device name'] in self.streamers[username]:
                    response = {"success": False,
                                "err": "Already viewing from this device"}
            if "err" not in response:
                session_id = str(uuid.uuid4())
                self.sessions[session_id] = username
                response = {"success": True, "session_id": session_id}
        else:
            response = {"success": False,
                                    "err": "Server is unavailable"}
        self.enc_socket.send_reply(client_socket, response)

    def handle_logout(self, request: dict):
        username = self.sessions.get(request["session_id"])
        self.send_data_to_all_viewers(username, {"type": "logout"})
        self.steamer_active[username] = False

    def handle_register(self, request: dict, client_socket: socket.socket):
        username = request["username"]
        password = request["password"]
        if not self.check_password(password) or not self.check_username(username):
            response = {"success": False, "msg": "Username and password must meet complexity requirments"}
        elif db.user_exists(username):
            response = {"success": False, "msg": "Username is taken"}
        elif db.insert_user(username, password):
            response = {"success": True}
        else:
            response = {"success": False, "msg": "Server is unavailable"}

        self.enc_socket.send_reply(client_socket, response)

    def check_password(self, password):
        if len(password) < 8:
            return False
        upper = False
        lower=False
        sign=False
        digit = False
        for p in password:
            if p.isupper():
                upper = True
            elif p.islower():
                lower=True
            elif p.isdigit():
                digit = True
            else:
                sign=True
        return upper and lower and digit and sign
    
    def check_username(self, username):
        return len(username)>=6

    def handle_get_devices(self, request: dict, client_socket: socket.socket):
        username = self.sessions.get(request["session_id"])
        viewers = list(self.streamers[username].keys())
        response = {"devices": viewers}
        self.enc_socket.send_reply(client_socket, response)

    def handle_register_viewer(self, request: dict, client_socket: socket.socket):
        username = self.sessions.get(request["session_id"])
        device_name = request['device name']
        if request['socket type'] == 'screenshots':
            self.streamers[username][device_name] = {
                'sockets': [client_socket],
                'active': False
            }

        response = {"success": True}
        self.enc_socket.send_reply(client_socket, response)

    def remove_pc_name_by_socket(self, target_socket):        
        for username, pc_dict in self.streamers.items():
            for pc_name, pc_data in pc_dict.items():
                if target_socket in pc_data['sockets']:
                    del self.streamers[username][pc_name]
                    return

    def handle_toggle_device(self, request: dict):
        username = self.sessions.get(request["session_id"])
        device_name = request['device name']
        active = request['active']
        self.streamers[username][device_name]['active'] = active
        if active:
            print('start')
            self.enc_socket.send_reply(
                self.streamers[username][device_name]['sockets'][0], {'type': 'start'})
        else:
            self.enc_socket.send_reply(
                self.streamers[username][device_name]['sockets'][0], {'type': 'stop'})

    def handle_client_screenshot(self, request: dict, client_socket):
        username = self.sessions.get(request["session_id"])
        if not self.steamer_active[username]:
            client_socket.close()
            return
        
        screenshot_data = {
            "type": "screenshot",
            "screenshot": request['screenshot']
        }

        self.send_data_to_active_viewers(username, screenshot_data, 'screenshot')

    def send_data_to_active_viewers(self, username: str, data: dict, type: str = 'screenshot'):
        user_devices = self.streamers.get(username)       
        if user_devices is not None:
            for pc_name, device_info in user_devices.items():
                if device_info.get('active', False):
                    sockets = device_info.get('sockets')
                    socket = sockets[0]
                    if socket is not None:
                        try:                            
                            self.enc_socket.send_reply(socket, data)
                        except:
                            del user_devices[pc_name]

    def send_data_to_all_viewers(self, username: str, data: dict, type: str = 'screenshot'):
        user_devices = self.streamers.get(username)       
        if user_devices is not None:
            for pc_name, device_info in user_devices.items():
                sockets = device_info.get('sockets')
                socket = sockets[0]
                if socket is not None:
                    try:                            
                        self.enc_socket.send_reply(socket, data)
                    except:
                        del user_devices[pc_name]