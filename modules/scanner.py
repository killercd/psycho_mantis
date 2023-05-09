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

class ScannerWindow(QWidget):
    def __init__(self, parent, tabs):
        super().__init__(parent)
        self.tabs = tabs
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Scanner')
        self.tabs.addTab(self, 'Scanner')

        layout = QFormLayout()

        self.txt_range_ip = QLineEdit()
        boxip = QHBoxLayout()
        boxip.addWidget(self.txt_range_ip)
        layout.addRow(QLabel("IP Range: "), boxip)

        

        self.setLayout(layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    server = ScannerWindow()
    server.show()
    sys.exit(app.exec_())