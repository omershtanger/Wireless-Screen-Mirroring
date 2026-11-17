import subprocess

class Stream:
    def __init__(self, session_id):
        self.session_id = session_id

    def stream_video(self):
        command = ['python', 'video_streamer.py', self.session_id]
        subprocess.Popen(command)

