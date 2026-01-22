import sys
from PySide6.QtCore import QObject, Slot
from PySide6.QtWebSockets import QWebSocketServer
from PySide6.QtNetwork import QHostAddress
from PySide6.QtWidgets import QApplication

class MyServer(QObject):
    def __init__(self, port=12345):
        super().__init__()
        # Create server: Name of server, non-secure mode
        self.server = QWebSocketServer("MyServer", QWebSocketServer.NonSecureMode, self)
        
        # Listen on all available network interfaces
        if self.server.listen(QHostAddress.Any, port):
            print(f"Server started on port {port}. Waiting for client...")
        else:
            print("Server failed to start.")
        
        print(f"Server: {self.server.serverAddress().toString()}:{self.server.serverPort()}")

        self.server.newConnection.connect(self.on_new_connection)
        self.clients = []

    @Slot()
    def on_new_connection(self):
        # Get the socket for the new client
        client_socket = self.server.nextPendingConnection()
        client_socket.textMessageReceived.connect(self.process_message)
        client_socket.disconnected.connect(self.on_disconnected)
        
        self.clients.append(client_socket)
        print("A client just connected!")

    @Slot(str)
    def process_message(self, message):
        print(f"Client says: {message}")
        # Echo back to the client
        sender = self.sender()
        sender.sendTextMessage(f"Server received: {message}")

    @Slot()
    def on_disconnected(self):
        client = self.sender()
        self.clients.remove(client)
        print("Client disconnected.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    server = MyServer()
    sys.exit(app.exec())