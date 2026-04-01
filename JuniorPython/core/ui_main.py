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
        self.setWindowTitle("PyForge Suite // JuniorCloud LLC")
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

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(250)
        self.sidebar.currentRowChanged.connect(self.switch_tool)
        layout.addWidget(self.sidebar)

        # Tool Container
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, 1)

    def load_tools(self):
        self.sidebar.clear()
        while self.stack.count() > 0:
            widget = self.stack.widget(0)
            self.stack.removeWidget(widget)
            widget.deleteLater()
        self.tools_registry.clear()

        if not self.tools_dir.exists():
            self.tools_dir.mkdir(parents=True)

        for filename in sorted(os.listdir(self.tools_dir)):
            if filename.endswith(".py") and filename != "__init__.py":
                self._import_tool(filename)

    def _import_tool(self, filename):
        module_name = filename[:-3]
        filepath = self.tools_dir / filename
        
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, BaseTool) and obj is not BaseTool:
                tool_instance = obj()
                tool_instance.set_context(self)
                tool_instance.setup_ui()
                
                tool_name = obj.get_name()
                self.tools_registry[tool_name] = tool_instance
                self.sidebar.addItem(tool_name)
                self.stack.addWidget(tool_instance)

    def switch_tool(self, index):
        if index >= 0:
            self.stack.setCurrentIndex(index)