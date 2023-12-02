import sys
import socket
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
import re
from PyQt5.QtCore import QProcess,Qt
import webbrowser

from PyQt5.QtWidgets import (QApplication, 
                             QWidget, 
                             QLabel, 
                             QHBoxLayout, 
                             QVBoxLayout,
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
                             QDialog,
                             QComboBox
                             )

from PyQt5.QtCore import QThread, pyqtSignal


class NmapScannerThread(QThread):
    finished = pyqtSignal()

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            result = subprocess.run(self.command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = result.stdout + result.stderr
            self.output = output
        except subprocess.CalledProcessError as e:
            self.output = f"Errore nell'esecuzione del comando: {e}"

        self.finished.emit()




class PopupDialogGenerateAgent(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle('SSH Brute')

        self.setGeometry(0, 0, 700, 400)
        self.form_layout = QFormLayout()
        self.main_window = parent
        

class PopupDialogHTTPRequester(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle('HTTP Requester')

        self.setGeometry(0, 0, 700, 400)
        self.main_window = parent

        v_layout = QVBoxLayout()
        

        host_box_layout = QHBoxLayout()
        txt_host = QLineEdit()
        txt_host.setFixedWidth(100)

        txt_port = QLineEdit()
        txt_port.setFixedWidth(30)

        host_box_layout.addWidget(txt_host)
        host_box_layout.addWidget(txt_port)
        host_box_layout.setAlignment(Qt.AlignLeft)

        resource_layout = QHBoxLayout()
        txt_resource = QLineEdit()

        menu_http_methods = QComboBox() 
        menu_http_methods.addItem("GET")
        menu_http_methods.addItem("HEAD")
        menu_http_methods.addItem("POST")
        menu_http_methods.addItem("PUT")
        menu_http_methods.addItem("DELETE")
        menu_http_methods.addItem("CONNECT")
        menu_http_methods.addItem("OPTIONS")
        menu_http_methods.addItem("TRACE")
        menu_http_methods.addItem("PATCH")

        resource_layout.addWidget(menu_http_methods)
        resource_layout.addWidget(txt_resource)

        v_layout.addLayout(host_box_layout)
        v_layout.addLayout(resource_layout)
        
        v_layout.setAlignment(Qt.AlignTop)
        self.setLayout(v_layout)




class ScannerWindow(QWidget):
    def __init__(self, parent, tabs):
        super().__init__(parent)
        self.tabs = tabs
        self.init_ui()

    def start_scanner(self):
        
        self.txt_output.clear()
        self.tree_result.clear()
        self.process.start("nmap -sV -T5 --open {}".format(self.txt_range_ip.text()))
        
         
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
    def get_service(self, output):
        if (output.find("tcp")>=0 or output.find("udp")>=0) and output.find("open")>=0:
            return output.split()[2:]
            
        return None

    def update_output(self):
        output = self.process.readAllStandardOutput().data().decode()
        error_output = self.process.readAllStandardError().data().decode()
        if output:
            
            for out_line in output.splitlines():
                ip = self.get_target(out_line)
                port = self.get_port(out_line)
                service = self.get_service(out_line)
                
                if ip:
                    new_ip = QTreeWidgetItem([ip])
                    self.last_ip = new_ip
                    self.tree_result.addTopLevelItem(new_ip)
                
                if port:
                    if self.last_ip:
                        port_result = port+"\t"+" ".join(service)
                        res_item = QTreeWidgetItem([port_result])
                        res_item.setToolTip(0, port_result)
                        self.last_ip.addChild(res_item)
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
    def http_requester(self, item):
        popup = PopupDialogHTTPRequester(self)
        popup.show()

    def open_in_browser(self, item):
        print("Open in browser:", item.text(0), item.text(1))
        print(item.parent().text(0))
        url = item.parent().text(0)+":"+item.text(0).split("/")[0]   

        webbrowser.open(url)


    def show_context_menu(self, position):
        item = self.tree_result.itemAt(position)
        
        if item is not None:
            menu = QMenu(self)
            ssh_bruteforce_action = QAction("SSH Brute", self)
            ssh_bruteforce_action.triggered.connect(lambda: self.ssh_brute(item))
            
            open_browser_action = QAction("Open in browser", self)
            open_browser_action.triggered.connect(lambda: self.open_in_browser(item))

            http_requester_action = QAction("HTTP Requester", self)
            http_requester_action.triggered.connect(lambda: self.http_requester(item))

            menu.addAction(ssh_bruteforce_action)
            menu.addAction(open_browser_action)
            menu.addAction(http_requester_action)

            menu.exec_(self.tree_result.viewport().mapToGlobal(position))


    def init_ui(self):
        self.setWindowTitle('Scanner')
        self.tabs.addTab(self, 'Scanner')
        self.scan_result = {}

        layout = QFormLayout()

        self.txt_range_ip = QLineEdit()
        self.txt_range_ip.returnPressed.connect(self.start_scanner)
        boxip = QHBoxLayout()
        boxip.addWidget(self.txt_range_ip)
        layout.addRow(QLabel("IP Range: "), boxip)

        result_box = QHBoxLayout()
        self.tree_result = QTreeWidget()
        self.tree_result.setFixedWidth(300)
        # self.tree_result.setColumnCount(1)
        self.tree_result.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_result.customContextMenuRequested.connect(self.show_context_menu)
        self.tree_result.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        result_box.addWidget(self.tree_result)
        

        self.txt_output = QTextEdit()
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