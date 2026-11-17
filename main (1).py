import os
from viewair_server import Server

def main():
    # Set the working directory to the server directory
    current_script_path = os.path.abspath(__file__)
    server_directory = os.path.dirname(current_script_path)
    os.chdir(server_directory)
    
    server = Server()
    server.accept_connections()

main()