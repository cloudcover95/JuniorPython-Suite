from PySide6.QtWidgets import QVBoxLayout, QPlainTextEdit, QPushButton, QHBoxLayout, QSplitter
from PySide6.QtCore import Qt, QProcess
from PySide6.QtGui import QTextCharFormat, QColor, QFont
from core.base_tool import BaseTool
from core.sandbox import SandboxExecutor
import os

class PythonSyntaxHighlighter:
    # Lightweight pseudo-Pygments implementation for fallback if pip fails
    pass

class TerminalEditorTool(BaseTool):
    """
    Professional Integrated Development Environment Pane.
    """
    @classmethod
    def get_name(cls):
        return "💻 Terminal & Editor"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Vertical)
        
        # Editor Top
        self.editor = QPlainTextEdit()
        font = QFont("Consolas", 12)
        self.editor.setFont(font)
        self.editor.setPlaceholderText("# Write rigorous Python manifold logic here...\n# E.g. vectorized MLX arrays or Pandas parquet ingests.")
        
        # Action Bar
        action_layout = QHBoxLayout()
        btn_run_sandbox = QPushButton("Run (Sandbox)")
        btn_run_sandbox.setStyleSheet("background-color: #2e8b57;")
        btn_run_sandbox.clicked.connect(self.run_sandboxed)
        
        btn_run_host = QPushButton("Run (Host)")
        btn_run_host.clicked.connect(self.run_host)
        
        btn_llm = QPushButton("Send to LLM")
        
        action_layout.addWidget(btn_run_sandbox)
        action_layout.addWidget(btn_run_host)
        action_layout.addWidget(btn_llm)
        action_layout.addStretch()
        
        # Terminal Emulation Bottom
        self.terminal = QPlainTextEdit()
        self.terminal.setFont(font)
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("background-color: #0c0c0c; color: #cccccc;")
        self.terminal.appendPlainText(">> PyForge PTY Emulator Initialized. Hardware: njr_local i5 / RTX 3060.")
        
        # Process Wrapper for real terminal integration
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)

        splitter.addWidget(self.editor)
        splitter.addWidget(self.terminal)
        splitter.setSizes([500, 300])
        
        layout.addLayout(action_layout)
        layout.addWidget(splitter)

    def run_sandboxed(self):
        if not self.app_context.sandbox_enabled:
            self.terminal.appendPlainText("\n[WARN] Sandbox toggle is bypassed globally. Refusing sandboxed request.")
            return
            
        code = self.editor.toPlainText()
        self.terminal.appendPlainText("\n>> [SANDBOX EXECUTION START]")
        executor = SandboxExecutor()
        result = executor.execute(code)
        
        if result.get('status') == 'SUCCESS':
            self.terminal.appendPlainText(result.get('output', ''))
        else:
            self.terminal.appendPlainText(f"[KERNEL FAULT] {result.get('status')}\n{result.get('output', '')}")
            
    def run_host(self):
        self.terminal.appendPlainText("\n>> [HOST EXECUTION START]")
        tmp_path = "temp_execution.py"
        with open(tmp_path, "w") as f:
            f.write(self.editor.toPlainText())
            
        self.process.start("python", [tmp_path])

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode()
        self.terminal.insertPlainText(data)
        self.terminal.ensureCursorVisible()

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode()
        self.terminal.insertPlainText(data)
        self.terminal.ensureCursorVisible()