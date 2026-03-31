import os
import sys
import importlib.util
import inspect
from pathlib import Path
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QListWidget, 
                               QStackedWidget, QVBoxLayout, QLabel)
from PySide6.QtCore import Qt
from core.base_tool import BaseTool

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JuniorPython Suite v1.0 // JuniorCloud LLC")
        self.app_id = "juniorpython_local_v1"
        self.tools_dir = Path(__file__).parent.parent / "tools"
        self.tools_registry = {}

        self._init_ui()
        self.load_tools()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar with JuniorCloud Branding
        self.sidebar_container = QVBoxLayout()
        self.brand_label = QLabel("JUNIORPYTHON")
        self.brand_label.setStyleSheet("font-weight: bold; color: #007acc; padding: 10px; font-size: 16px;")
        
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar.currentRowChanged.connect(self.switch_tool)
        
        self.sidebar_container.addWidget(self.brand_label)
        self.sidebar_container.addWidget(self.sidebar)
        layout.addLayout(self.sidebar_container)

        # Tool Container
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

    def load_tools(self):
        self.sidebar.clear()
        while self.stack.count() > 0:
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()
        
        # Priority Load: Security Shield first
        tool_files = sorted([f for f in os.listdir(self.tools_dir) if f.endswith(".py") and f != "__init__.py"])
        for filename in tool_files:
            self._import_tool(filename)

    def _import_tool(self, filename):
        module_name = filename[:-3]
        filepath = self.tools_dir / filename
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BaseTool) and obj is not BaseTool:
                instance = obj()
                instance.set_context(self)
                instance.setup_ui()
                self.tools_registry[obj.get_name()] = instance
                self.sidebar.addItem(obj.get_name())
                self.stack.addWidget(instance)

    def switch_tool(self, index):
        if index >= 0:
            self.stack.setCurrentIndex(index)