# JuniorPython/tools/10_script_hunter.py
import os
import shutil
import urllib.request
import urllib.error
from pathlib import Path
from PySide6.QtWidgets import (QVBoxLayout, QTreeView, QFileSystemModel, 
                               QSplitter, QPlainTextEdit, QPushButton, QHBoxLayout, 
                               QLabel, QTabWidget, QWidget, QLineEdit, QListWidget)
from PySide6.QtCore import QDir, Qt, QThread, Signal
from core.base_tool import BaseTool
from core.sandbox import SandboxExecutor
import ollama

class LlamaAuditThread(QThread):
    """Isolated neural thread for auditing remote vectors prior to execution."""
    audit_complete = Signal(str)
    
    def __init__(self, code_payload):
        super().__init__()
        self.code_payload = code_payload

    def run(self):
        prompt = (
            "Analyze the following Python script for malicious intent, "
            "infinite loops, or destructive I/O operations. Provide a dense, "
            "technical summary of its geometry and safety.\n\n"
            f"```python\n{self.code_payload}\n```"
        )
        try:
            res = ollama.chat(model='llama3.2:3b', messages=[{'role': 'user', 'content': prompt}])
            self.audit_complete.emit(res['message']['content'])
        except Exception as e:
            self.audit_complete.emit(f"[HARDWARE FAULT] Neural inference failed: {str(e)}")

class ScriptHunterTool(BaseTool):
    """
    Filesystem and remote repository analysis tensor.
    Locates, audits, sandboxes, and injects external Python scripts into the core manifold.
    """
    @classmethod
    def get_name(cls):
        return "🔍 Script Hunter"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel: Source Tabs (Local vs Remote)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0,0,0,0)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { background: #2d2d30; padding: 8px; } QTabBar::tab:selected { background: #007acc; }")
        
        # Tab 1: Local Topology
        local_tab = QWidget()
        local_tab_layout = QVBoxLayout(local_tab)
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.model.setNameFilters(["*.py"])
        self.model.setNameFilterDisables(False)
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(QDir.currentPath()))
        self.tree.setColumnWidth(0, 200)
        self.tree.clicked.connect(self.preview_local_script)
        local_tab_layout.addWidget(QLabel("Discover Local .py Vectors:"))
        local_tab_layout.addWidget(self.tree)
        self.tabs.addTab(local_tab, "Local Node")
        
        # Tab 2: Remote Repository (GitHub / Open Source)
        remote_tab = QWidget()
        remote_tab_layout = QVBoxLayout(remote_tab)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://raw.githubusercontent.com/...")
        btn_fetch = QPushButton("Fetch Remote Vector")
        btn_fetch.clicked.connect(self.fetch_remote_script)
        
        self.curated_list = QListWidget()
        self.curated_list.addItem("https://raw.githubusercontent.com/psf/requests/main/requests/api.py")
        self.curated_list.addItem("https://raw.githubusercontent.com/pallets/flask/main/src/flask/app.py")
        self.curated_list.itemClicked.connect(lambda item: self.url_input.setText(item.text()))
        
        remote_tab_layout.addWidget(QLabel("Ingest Open-Source Raw Targets:"))
        remote_tab_layout.addWidget(self.url_input)
        remote_tab_layout.addWidget(btn_fetch)
        remote_tab_layout.addWidget(QLabel("Curated / History:"))
        remote_tab_layout.addWidget(self.curated_list)
        self.tabs.addTab(remote_tab, "Remote Hub")
        
        left_layout.addWidget(self.tabs)
        
        # Right Panel: Preview, Audit, & Actions
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0,0,0,0)
        
        self.preview = QPlainTextEdit()
        self.preview.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; font-family: 'Consolas';")
        
        self.audit_log = QPlainTextEdit()
        self.audit_log.setReadOnly(True)
        self.audit_log.setMaximumHeight(150)
        self.audit_log.setStyleSheet("background-color: #0c0c0c; color: #00ff41; font-family: 'Consolas'; border: 1px solid #333;")
        self.audit_log.setPlaceholderText("Neural Audit Stream Output...")
        
        action_bar = QHBoxLayout()
        btn_audit = QPushButton("Neural Audit (LLM)")
        btn_audit.setStyleSheet("background-color: #512da8;")
        btn_audit.clicked.connect(self.audit_script)
        
        btn_run = QPushButton("Execute in Sandbox")
        btn_run.setStyleSheet("background-color: #0e639c;")
        btn_run.clicked.connect(self.sandbox_execute)
        
        btn_load = QPushButton("Inject to Core Tools")
        btn_load.setStyleSheet("background-color: #2e8b57;")
        btn_load.clicked.connect(self.inject_as_tool)
        
        action_bar.addWidget(btn_audit)
        action_bar.addWidget(btn_run)
        action_bar.addWidget(btn_load)
        
        right_layout.addWidget(QLabel("Script Tensor Preview:"))
        right_layout.addWidget(self.preview)
        right_layout.addWidget(self.audit_log)
        right_layout.addLayout(action_bar)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([350, 650])
        
        layout.addWidget(splitter)
        self.current_filepath = None
        self.current_filename = "fetched_tool.py"

    def preview_local_script(self, index):
        path = self.model.filePath(index)
        if not os.path.isdir(path) and path.endswith(".py"):
            if not self.is_safe(path):
                self.preview.setPlainText("# [SECURITY LOCK] Cannot read from protected manifold.")
                return
            self.current_filepath = path
            self.current_filename = os.path.basename(path)
            with open(path, 'r', encoding='utf-8') as f:
                self.preview.setPlainText(f.read())
            self.audit_log.clear()

    def fetch_remote_script(self):
        url = self.url_input.text().strip()
        if not url: return
        
        self.audit_log.setPlainText(f">> Initializing HTTP GET request to: {url}")
        try:
            # Lean utility tier: urllib bypasses requests bloat
            req = urllib.request.Request(url, headers={'User-Agent': 'JuniorPython/2.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                code_payload = response.read().decode('utf-8')
                self.preview.setPlainText(code_payload)
                self.current_filepath = None
                self.current_filename = url.split('/')[-1]
                if not self.current_filename.endswith('.py'):
                    self.current_filename += ".py"
                self.audit_log.appendPlainText(f"[SUCCESS] Payload ingested. {len(code_payload)} bytes active in memory.")
        except urllib.error.URLError as e:
            self.audit_log.appendPlainText(f"[NETWORK FAULT] Unresolved vector: {e.reason}")

    def audit_script(self):
        code = self.preview.toPlainText()
        if not code: return
        self.audit_log.setPlainText(">> Compiling context array for Local LLM (llama3.2:3b)...")
        
        self.thread = LlamaAuditThread(code)
        self.thread.audit_complete.connect(self._render_audit)
        self.thread.start()

    def _render_audit(self, response):
        self.audit_log.appendPlainText("\n[AUDIT COMPLETE]")
        self.audit_log.appendPlainText(response)
        # Log to pipeline for architectural records
        self.pipeline.append_log("security_audits", {"filename": self.current_filename, "audit": response})

    def inject_as_tool(self):
        code = self.preview.toPlainText()
        if not code: return
        
        # Format filename to ensure sorting within the module manifold
        dest_name = f"99_{self.current_filename}"
        dest_path = self.app_context.tools_dir / dest_name
        
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(code)
            
        self.audit_log.appendPlainText(f">> File mirrored to core topology: {dest_path}")
        self.app_context.load_tools()

    def sandbox_execute(self):
        code = self.preview.toPlainText()
        if not code: return
        
        executor = SandboxExecutor()
        self.audit_log.appendPlainText("\n>> [SANDBOX] Dispatching script execution tensor...")
        result = executor.execute(code)
        
        if result.get('status') == 'SUCCESS':
            self.audit_log.appendPlainText(f"[RESULT]\n{result.get('output')}")
        else:
            self.audit_log.appendPlainText(f"[KERNEL FAULT] {result.get('status')}\n{result.get('output')}")