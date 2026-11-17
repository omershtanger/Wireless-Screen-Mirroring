import queue
import threading
import encrypted_socket

class Streamer:
    def __init__(self, session_id):
        self.session_id = session_id
        self.stop_threads = False
        self.queue = queue.Queue()

        self.socket = encrypted_socket.EncryptedSocket()
        self.socket.connect()

        record_thread = threading.Thread(target=self.capture)
        record_thread.start()
        send_thread = threading.Thread(target=self.send)
        send_thread.start()
        print('Streaming started')

    def capture(self):
        raise NotImplementedError("Subclasses must override capture method")

    def send(self):
        raise NotImplementedError("Subclasses must override send method")