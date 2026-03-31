from PySide6.QtWidgets import (QVBoxLayout, QTreeView, QFileSystemModel, 
                               QSplitter, QPlainTextEdit, QPushButton, QHBoxLayout, QLabel)
from PySide6.QtCore import QDir, Qt
import os
import shutil
from core.base_tool import BaseTool
from core.sandbox import SandboxExecutor

class ScriptHunterTool(BaseTool):
    """
    Filesystem analysis tensor for locating, sandboxing, and injecting python scripts.
    """
    @classmethod
    def get_name(cls):
        return "🔍 Script Hunter"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side: File Tree
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0,0,0,0)
        
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.model.setNameFilters(["*.py"])
        self.model.setNameFilterDisables(False)
        
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(QDir.currentPath()))
        self.tree.setColumnWidth(0, 200)
        self.tree.clicked.connect(self.preview_script)
        
        left_layout.addWidget(QLabel("Discover .py Vectors:"))
        left_layout.addWidget(self.tree)
        
        # Right side: Preview & Actions
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0,0,0,0)
        
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setStyleSheet("background-color: #1e1e1e; font-family: 'Consolas';")
        
        action_bar = QHBoxLayout()
        btn_load = QPushButton("Load as Tool")
        btn_run = QPushButton("Run in Sandbox")
        btn_analyze = QPushButton("Analyze with LLM")
        
        btn_load.clicked.connect(self.inject_as_tool)
        btn_run.clicked.connect(self.sandbox_execute)