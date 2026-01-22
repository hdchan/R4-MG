import sys
from PySide6.QtCore import QUrl, Slot, QTimer
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtWidgets import QApplication

class MyClient(QWebSocket):
    def __init__(self, server_ip):
        super().__init__()
        self.connected.connect(self.on_connect)
        self.textMessageReceived.connect(self.on_message)
        
        # Connect to the server's IP and port
        print(f"Connecting to {server_ip}...")
        self.open(QUrl(f"ws://{server_ip}:12345"))

    @Slot()
    def on_connect(self):
        print("Connected! Sending a 'Hello'...")
        self.sendTextMessage("Hello from the other computer!")

    @Slot(str)
    def on_message(self, message):
        print(f"Reply from Server: {message}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # REPLACE with Computer A's IP address
    client = MyClient("127.0.0.1") 
    sys.exit(app.exec())