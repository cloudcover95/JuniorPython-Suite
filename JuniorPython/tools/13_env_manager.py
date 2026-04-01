from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QListWidget, QLineEdit, QHBoxLayout, QTextEdit
from core.base_tool import BaseTool
import subprocess
import sys
import threading

class EnvManagerTool(BaseTool):
    """
    Dependency matrix management. Installs and uninstalls pip packages locally.
    """
    @classmethod
    def get_name(cls):
        return "🐍 Env Matrix (PIP)"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        header = QLabel(f"Python Subsystem: {sys.executable}")
        header.setStyleSheet("color: #00ff00; font-weight: bold;")
        
        control_layout = QHBoxLayout()
        self.pkg_input = QLineEdit()
        self.pkg_input.setPlaceholderText("Enter package name (e.g., polars)")
        
        btn_install = QPushButton("Install Package")
        btn_install.clicked.connect(lambda: self.run_pip("install"))
        
        btn_list = QPushButton("Refresh Matrix")
        btn_list.clicked.connect(lambda: self.run_pip("list"))
        
        control_layout.addWidget(self.pkg_input)
        control_layout.addWidget(btn_install)
        control_layout.addWidget(btn_list)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background-color: #000; color: #fff; font-family: 'Consolas';")
        
        layout.addWidget(header)
        layout.addLayout(control_layout)
        layout.addWidget(self.console)
        
        # Initial scan
        self.run_pip("list")

    def run_pip(self, cmd):
        pkg = self.pkg_input.text()
        
        args = [sys.executable, "-m", "pip", cmd]
        if cmd == "install" and pkg:
            args.append(pkg)
            self.console.append(f">> Modifying local topology: pip install {pkg}...")
        elif cmd == "install" and not pkg:
            return
            
        threading.Thread(target=self._exec_pip, args=(args,), daemon=True).start()
        self.pkg_input.clear()

    def _exec_pip(self, args):
        try:
            result = subprocess.run(args, capture_output=True, text=True, check=True)
            self.console.append(result.stdout)
        except subprocess.CalledProcessError as e:
            self.console.append(f"[KERNEL FAULT] Exit Code {e.returncode}\n{e.stderr}")