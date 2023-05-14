import sys
import socket
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
import re
from PyQt5.QtCore import QProcess

from PyQt5.QtWidgets import (QApplication, 
                             QWidget, 
                             QLabel, 
                             QHBoxLayout, 
                             QTextEdit, 
                             QLineEdit, 
                             QPushButton, 
                             QTabWidget,
                             QTreeWidgetItem,
                             QTreeWidget,
                             QFormLayout,
                             QMenu,
                             QAction,
                             QFileDialog,
                             QDialog
                             )

class PopupDialogGenerateAgent(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle('SSH Brute')

        self.setGeometry(0, 0, 600, 400)
        self.form_layout = QFormLayout()
        self.main_window = parent

        



class ScannerWindow(QWidget):
    def __init__(self, parent, tabs):
        super().__init__(parent)
        self.tabs = tabs
        self.init_ui()

    def start_scanner(self):
        
        self.txt_output.clear()
        self.tree_result.clear()
        self.process.start("nmap -sV -O -T5 --open {}".format(self.txt_range_ip.text()))
        
         
    def get_target(self, output):
        if output.find("Nmap scan report for")>=0:
            match = re.search(r'\((.*?)\)', output)
            if match:
                return match.group(1)
        return None
    
    def get_port(self, output):
        if (output.find("tcp")>=0 or output.find("udp")>=0) and output.find("open")>=0:
            
            match = re.search(r'[\d]+\/(tcp|udp)',output)
            if match:
                return match.group()
            
        return None

    def update_output(self):
        output = self.process.readAllStandardOutput().data().decode()
        error_output = self.process.readAllStandardError().data().decode()
        if output:
            
            for out_line in output.splitlines():
                ip = self.get_target(out_line)
                port = self.get_port(out_line)
                
                if ip:
                    new_ip = QTreeWidgetItem([ip])
                    self.last_ip = new_ip
                    self.tree_result.addTopLevelItem(new_ip)
                
                if port:
                    if self.last_ip:
                        self.last_ip.addChild(QTreeWidgetItem([port]))
        if output:
            self.txt_output.append(output)
        if error_output:
            self.txt_output.append(error_output)

    def ssh_brute(self, item):
        print("SSHBrute:", item.text(0), item.text(1))
        popup = PopupDialogGenerateAgent(self)
        popup.show()
        # fileDialog = QFileDialog(self)
        # fileDialog.setFileMode(QFileDialog.ExistingFile)
        # fileDialog.setOption(QFileDialog.ReadOnly, True)

    def show_context_menu(self, position):
        item = self.tree_result.itemAt(position)
        
        if item is not None:
            menu = QMenu(self)
            ssh_bruteforce_action = QAction("SSH Brute", self)
            ssh_bruteforce_action.triggered.connect(lambda: self.ssh_brute(item))

            menu.addAction(ssh_bruteforce_action)
            menu.exec_(self.tree_result.viewport().mapToGlobal(position))


    def init_ui(self):
        self.setWindowTitle('Scanner')
        self.tabs.addTab(self, 'Scanner')

        layout = QFormLayout()

        self.txt_range_ip = QLineEdit()
        boxip = QHBoxLayout()
        boxip.addWidget(self.txt_range_ip)
        layout.addRow(QLabel("IP Range: "), boxip)

        result_box = QHBoxLayout()
        self.tree_result = QTreeWidget()
        self.tree_result.setFixedWidth(200)
        self.tree_result.setColumnCount(1)
        self.tree_result.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_result.customContextMenuRequested.connect(self.show_context_menu)

        result_box.addWidget(self.tree_result)
        

        self.txt_output = QTextEdit()
        self.txt_output.setStyleSheet("background-color: black; color: white; font-size: 10pt;")
        result_box.addWidget(self.txt_output)
        layout.addRow(result_box)

        self.btn_start = QPushButton("Start")
        self.btn_start.clicked.connect(self.start_scanner)
        self.btn_start.setFixedWidth(100)
        button_box = QHBoxLayout()
        button_box.setAlignment(Qt.AlignRight)
        button_box.addWidget(self.btn_start)
        
        layout.addRow(button_box)
        self.setLayout(layout)


        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.update_output)
        self.process.readyReadStandardError.connect(self.update_output)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    server = ScannerWindow()
    server.show()
    sys.exit(app.exec_())