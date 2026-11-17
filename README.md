# ViewAir: Wireless Screen Mirroring

ViewAir is a Python desktop app that mirrors a computer's screen wirelessly, in real time, to other computers on the same local network. One user mirrors their screen, and they choose which connected devices receive it. All traffic between the clients and the server is encrypted with TLS.

<!-- Add screenshots or a demo GIF here, e.g. ![ViewAir](images/demo.gif) -->

## Features

- **Real-time screen streaming:** the screen is captured, compressed to JPEG and streamed to viewers at about 8 FPS.
- **Two roles:** **Mirror** (shares the screen) and **Viewer** (displays it).
- **Device selection:** the mirroring user sees every connected viewer and turns streaming on or off for each device separately.
- **Encrypted communication:** all sockets are wrapped in TLS (SSL).
- **User accounts:** sign up and log in, with passwords hashed using bcrypt and stored in SQLite.
- **Password policy:** passwords need at least 8 characters, with upper-case and lower-case letters, a digit and a symbol. Usernames need at least 6 characters.
- **Display modes:** viewers can switch between a small always-on-top **Mini Player** and **Full Screen**.
- **Session management:** each login gets a unique session ID, and the server stops a user from mirroring twice from the same account or viewing twice from the same device.
- **Modern GUI:** a dark-themed interface built with CustomTkinter.

## Architecture

```
┌──────────────┐        TLS         ┌─────────────────────┐        TLS        ┌──────────────┐
│ Mirror client│ ─── screenshots ─► │       Server        │ ── screenshots ─► │ Viewer client│
│ (screen cap) │ ◄── device list ── │  multithreaded,     │                   │  (display)   │
└──────────────┘                    │  sessions, SQLite   │ ── screenshots ─► ┌──────────────┐
                                    └─────────────────────┘                   │ Viewer client│
                                                                              └──────────────┘
```

**Server**
- Accepts TLS connections and handles each client in its own thread.
- Tracks the active sessions, the mirroring users and the viewer devices registered to each user.
- Forwards screen frames only to the viewer devices the mirroring user has turned on.

**Client**
- **Mirror:** captures the screen with a producer-consumer design. One thread captures and compresses frames into a queue, and another thread sends them to the server.
- **Viewer:** registers its device with the server and renders the incoming frames on a Tkinter canvas.

### Communication Protocol

Messages are JSON objects, each sent with a **4-byte big-endian length prefix**. This lets the receiver read exactly one full message from the TCP stream. Each message has a `type`, such as:

| Type | Purpose |
|---|---|
| `register` / `login` / `logout` | Account and session handling |
| `register viewer` | A viewer device registers to receive frames |
| `get devices` | The mirror asks for the list of connected viewers |
| `toggle device` | Turns streaming to a specific viewer on or off |
| `client screenshot` | A frame sent from the mirror to the server |
| `screenshot` / `start` / `stop` | Messages sent from the server to viewers |

## Project Structure

```
ViewAir/
├── server/
│   ├── main.py               # Server entry point
│   ├── viewair_server.py     # Connection handling, sessions, routing frames
│   ├── db.py                 # SQLite user database + bcrypt hashing
│   ├── encrypted_socket.py   # TLS server socket + length-prefixed JSON
│   └── constants.py          # IP, port, certificate and DB settings
├── client/
│   ├── main.py               # Client entry point
│   ├── login_window.py       # Login screen (Mirror / Viewer)
│   ├── register_window.py    # Sign-up screen
│   ├── device_selection.py   # Mirror: choose which devices receive the stream
│   ├── viewer_window.py      # Viewer: display window and settings
│   ├── streamer.py           # Base class for capture/send threads
│   ├── video_streamer.py     # Screen capture, JPEG compression, sending
│   ├── stream.py             # Starts the streaming process
│   ├── encrypted_socket.py   # TLS client socket
│   └── constants.py          # Server IP and port
├── server.bat / client.bat / run.bat
```

## Tech Stack

Python · socket · ssl (TLS) · threading · SQLite · bcrypt · CustomTkinter / Tkinter · Pillow · PyAutoGUI

## Getting Started

> ViewAir runs on **Windows**, because the viewer uses `netsh` and `wmi` to show network information.

1. **Clone the repository**
   ```bash
   git clone https://github.com/omershtanger/ViewAir.git
   cd ViewAir
   ```

2. **Install the dependencies**
   ```bash
   pip install customtkinter pillow pyautogui bcrypt psutil wmi soundcard numpy
   ```

3. **Create a TLS certificate** for the server (in the `server/` folder):
   ```bash
   openssl req -x509 -newkey rsa:2048 -nodes -keyout server.key -out server.crt -days 365
   ```

4. **Set the server IP address:** change `SERVER_IP` in both `server/constants.py` and `client/constants.py` to the local IP of the computer that runs the server.

5. **Run the app**
   - `server.bat` starts the server.
   - `client.bat` starts a client. Run it on each computer.
   - `run.bat` starts the server and two clients on one computer, for testing.

6. **Use it**
   - Sign up and log in as **Mirror** on the computer that will share its screen.
   - Log in with the same account as **Viewer** on the other computers.
   - In the mirror's device list, click a device to start or stop streaming to it.

## Author

**Omer Shtanger**
