import sys
import socket
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import (QApplication, 
                             QWidget, 
                             QLabel, 
                             QHBoxLayout, 
                             QTextEdit, 
                             QLineEdit, 
                             QPushButton, 
                             QTabWidget,
                             QFormLayout)

class TcpServer(QThread):
    new_message = pyqtSignal(str)
    def __init__(self, iface, port):
        QThread.__init__(self)
        self.iface = iface
        self.port = port
        self.running = True
        self.client_socket = None
    
    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.iface, self.port))
        self.new_message.emit('Start server on {}:{}\r\n'.format(self.iface, str(self.port)))
        server_socket.listen(1)
        while self.running:
            self.client_socket, client_address = server_socket.accept()
            self.new_message.emit('Connected to {}:{}\r\n'.format(client_address[0], client_address[1]))
            while True:
                data = self.client_socket.recv(1024)
                if not data or len(data)<1:
                    break
                self.new_message.emit(data.decode())
            self.client_socket.close()
        server_socket.close()
    
    def stop(self):
        self.running = False
        self.new_message.emit('Stop server\r\n')

class ChatWindow(QWidget):
    def __init__(self, parent, iface,  port):
        super().__init__()
        self.parent = parent
        self.iface = iface
        self.port = port
        self.init_ui()
    
    def start_server(self):
        self.tcp_server = TcpServer(self.iface, self.port)
        self.tcp_server.new_message.connect(self.add_message)
        self.tcp_server.start()
    
    def stop_server(self):
        self.tcp_server.stop()

    def init_ui(self):
        

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_server)
        self.start_button.setFixedWidth(100)

        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_server)
        self.stop_button.setFixedWidth(100)
        
        self.message_box = QTextEdit(self)
        self.message_box.setReadOnly(True)
        self.message_box.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.message_box.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.message_box.setStyleSheet("background-color: black; color: white; font-size:10pt;")
        
        self.message_input = QLineEdit(self)
        self.send_button = QPushButton('Send', self)
        self.send_button.clicked.connect(self.send_message)
        
        layout = QFormLayout()
        
        box_button = QHBoxLayout()
        box_button.addWidget(self.start_button)
        box_button.addWidget(self.stop_button)

        layout.addRow(QLabel("Server: "), box_button)

        layout.addRow(self.message_box)

        hbox = QHBoxLayout()
        hbox.addWidget(self.message_input)
        hbox.addWidget(self.send_button)
        layout.addRow(hbox)

        self.setLayout(layout)

        
        # self.tcp_server = TcpServer(self.iface, self.port)
        # self.tcp_server.new_message.connect(self.add_message)
        # self.tcp_server.start()
    
    def add_message(self, message):
        self.message_box.moveCursor(QTextCursor.End)
        self.message_box.insertPlainText(message)
        self.message_box.ensureCursorVisible()
    
    def send_message(self):
        message = self.message_input.text()
        if message:
            self.add_message('Server: {}\n'.format(message))
            self.message_input.clear()
            message+="\n"
            self.tcp_server.client_socket.send(message.encode())
            
    def closeEvent(self, event):
        self.tcp_server.stop()
        event.accept()

class ChatServer(QTabWidget):
    def __init__(self, parent, tabs):
        super().__init__(parent)
        self.tabs = tabs
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Netcat')
        self.tabs.addTab(ChatWindow(self.tabs,"0.0.0.0", 4949), 'Netcat')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    server = ChatServer()
    server.show()
    sys.exit(app.exec_())
