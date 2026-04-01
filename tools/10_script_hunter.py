# JuniorPython/tools/10_script_hunter.py
import os
import shutil
import urllib.request
import urllib.error
import urllib.parse
import json
import re
from pathlib import Path
from PySide6.QtWidgets import (QVBoxLayout, QTreeView, QFileSystemModel, 
                               QSplitter, QPlainTextEdit, QPushButton, QHBoxLayout, 
                               QLabel, QTabWidget, QWidget, QLineEdit, QListWidget, QListWidgetItem)
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

class GitHubCrawlerThread(QThread):
    """
    Traverses Open Source GitHub repositories to extract .py tool vectors.
    Bypasses git bloat by leveraging the GitHub Git Database API.
    """
    tree_ready = Signal(list)
    error_signal = Signal(str)

    def __init__(self, repo_url):
        super().__init__()
        self.repo_url = repo_url

    def run(self):
        match = re.search(r'github\.com/([^/]+)/([^/]+)', self.repo_url)
        if not match:
            self.error_signal.emit("[KERNEL FAULT] Invalid GitHub repository topology.")
            return

        owner, repo = match.groups()
        repo = repo.replace('.git', '')

        try:
            # 1. Determine default branch topology
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            req = urllib.request.Request(api_url, headers={'User-Agent': 'JuniorPython-SDK'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                default_branch = data.get('default_branch', 'main')

            # 2. Extract repository tree recursively
            tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
            req = urllib.request.Request(tree_url, headers={'User-Agent': 'JuniorPython-SDK'})
            with urllib.request.urlopen(req, timeout=10) as response:
                tree_data = json.loads(response.read().decode())
                py_files = []
                for item in tree_data.get('tree', []):
                    if item['type'] == 'blob' and item['path'].endswith('.py'):
                        raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/{item['path']}"
                        py_files.append({"path": item['path'], "raw_url": raw_url})
                self.tree_ready.emit(py_files)

        except urllib.error.HTTPError as e:
            if e.code == 403:
                self.error_signal.emit("[NETWORK FAULT] API Rate Limit Exceeded. Await cooldown.")
            else:
                self.error_signal.emit(f"[NETWORK FAULT] HTTP {e.code}: {e.reason}")
        except Exception as e:
            self.error_signal.emit(f"[SYSTEM FAULT] Extraction failed: {str(e)}")

class ScriptHunterTool(BaseTool):
    """
    Filesystem and remote repository analysis tensor.
    Locates, audits, sandboxes, and injects external Python scripts into the core manifold.
    Consolidates web extraction specifically for tool generation.
    """
    @classmethod
    def get_name(cls):
        return "🔍 Script Hunter (Hub)"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel: Source Tabs (Local vs Remote)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0,0,0,0)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { background: #2d2d30; padding: 8px; color: #d4d4d4;} QTabBar::tab:selected { background: #007acc; font-weight: bold; }")
        
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
        
        self.repo_input = QLineEdit()
        self.repo_input.setPlaceholderText("https://github.com/logsv/llm-video-editor")
        
        btn_crawl = QPushButton("Crawl Repository Topology")
        btn_crawl.setStyleSheet("background-color: #0e639c; font-weight: bold;")
        btn_crawl.clicked.connect(self.crawl_remote_repo)
        
        self.remote_file_list = QListWidget()
        self.remote_file_list.itemClicked.connect(self.fetch_remote_script)
        
        remote_tab_layout.addWidget(QLabel("Ingest Open-Source Repository:"))
        remote_tab_layout.addWidget(self.repo_input)
        remote_tab_layout.addWidget(btn_crawl)
        remote_tab_layout.addWidget(QLabel("Discovered Tool Vectors (.py):"))
        remote_tab_layout.addWidget(self.remote_file_list)
        self.tabs.addTab(remote_tab, "Open-Source Hub")
        
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
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter)
        self.current_filepath = None
        self.current_filename = "fetched_tool.py"

    def preview_local_script(self, index):
        path = self.model.filePath(index)
        if not os.path.isdir(path) and path.endswith(".py"):
            # Enforce global vault constraints (Security Protocol IV)
            if hasattr(self, 'is_safe') and not self.is_safe(path):
                self.preview.setPlainText("# [SECURITY LOCK] Cannot read from protected manifold.")
                return
            self.current_filepath = path
            self.current_filename = os.path.basename(path)
            with open(path, 'r', encoding='utf-8') as f:
                self.preview.setPlainText(f.read())
            self.audit_log.clear()

    def crawl_remote_repo(self):
        repo_url = self.repo_input.text().strip()
        if not repo_url: return
        
        self.audit_log.setPlainText(f">> Mapping repository geometry: {repo_url}")
        self.remote_file_list.clear()
        
        self.crawler_thread = GitHubCrawlerThread(repo_url)
        self.crawler_thread.tree_ready.connect(self._populate_remote_tree)
        self.crawler_thread.error_signal.connect(lambda e: self.audit_log.appendPlainText(e))
        self.crawler_thread.start()

    def _populate_remote_tree(self, py_files):
        self.audit_log.appendPlainText(f"[SUCCESS] Extracted {len(py_files)} Python vectors.")
        for file_data in py_files:
            item = QListWidgetItem(file_data['path'])
            item.setData(Qt.UserRole, file_data['raw_url'])
            self.remote_file_list.addItem(item)

    def fetch_remote_script(self, item):
        raw_url = item.data(Qt.UserRole)
        self.current_filename = item.text().split('/')[-1]
        
        self.audit_log.setPlainText(f">> Ingesting raw vector: {raw_url}")
        try:
            req = urllib.request.Request(raw_url, headers={'User-Agent': 'JuniorPython-SDK'})
            with urllib.request.urlopen(req, timeout=5) as response:
                code_payload = response.read().decode('utf-8')
                self.preview.setPlainText(code_payload)
                self.current_filepath = None
                self.audit_log.appendPlainText(f"[SUCCESS] Payload ingested. {len(code_payload)} bytes active.")
        except urllib.error.URLError as e:
            self.audit_log.appendPlainText(f"[NETWORK FAULT] Unresolved vector: {e.reason}")

    def audit_script(self):
        code = self.preview.toPlainText()
        if not code: return
        self.audit_log.setPlainText(">> Compiling context array for Local Neural Engine...")
        
        self.thread = LlamaAuditThread(code)
        self.thread.audit_complete.connect(self._render_audit)
        self.thread.start()

    def _render_audit(self, response):
        self.audit_log.appendPlainText("\n[AUDIT COMPLETE]")
        self.audit_log.appendPlainText(response)
        if hasattr(self, 'pipeline'):
            self.pipeline.append_log("security_audits", {"filename": self.current_filename, "audit": response})

    def inject_as_tool(self):
        code = self.preview.toPlainText()
        if not code: return
        
        dest_name = f"99_{self.current_filename}"
        dest_path = self.app_context.tools_dir / dest_name
        
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(code)
            
        self.audit_log.appendPlainText(f">> Vector mirrored to core topology: {dest_path}")
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