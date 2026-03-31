from PySide6.QtWidgets import QVBoxLayout, QTextEdit, QPushButton, QHBoxLayout
from core.base_tool import BaseTool
import subprocess

class IDEFeaturesTool(BaseTool):
    @classmethod
    def get_name(cls):
        return "Py IDE Core"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Write execution logic here...")
        
        btn_run = QPushButton("Execute Matrix")
        btn_run.clicked.connect(self.run_code)
        
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(150)
        
        layout.addWidget(self.editor)
        layout.addWidget(btn_run)
        layout.addWidget(self.console)

    def run_code(self):
        code = self.editor.toPlainText()
        try:
            # Dangerous in prod, valid for local isolated environment script dev
            exec_locals = {}
            exec(code, globals(), exec_locals)
            self.console.append("Execution Standard: Code deployed to memory structure successfully.")
        except Exception as e:
            self.console.append(f"Traceback Topology: {str(e)}")