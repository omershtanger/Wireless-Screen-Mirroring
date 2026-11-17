import sys
import queue
import time
import pyautogui
import base64
import io
from PIL import Image
from streamer import Streamer


class VideoStreamer(Streamer):
    def __init__(self, session_id):
        super().__init__(session_id)
        self.fps=8

    def capture(self):
        while not self.stop_threads:
            try:
                frame = pyautogui.screenshot()
                img_io = io.BytesIO()
                frame.save(img_io, format='JPEG', quality=10)
                img_io.seek(0)
                img_bytes = img_io.read()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                self.queue.put(img_b64)
                time.sleep(1/self.fps)
            except Exception as e:
                pass

    def send(self):
        while not self.stop_threads:
            try:
                # Retrieve a screenshot frame from the queue
                self.img_b64 = self.queue.get()

                info = {
                    "type": "client screenshot",
                    "session_id": self.session_id,
                    "screenshot": self.img_b64
                }
                try:
                    self.socket.send_data(info)
                except:
                    pass
                time.sleep(1/self.fps)

            except queue.Empty:
                pass

session_id = sys.argv[1]
VideoStreamer(session_id)
