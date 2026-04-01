from PySide6.QtWidgets import QVBoxLayout, QTreeView, QFileSystemModel, QLabel
from PySide6.QtCore import QDir
from core.base_tool import BaseTool

class FileManagerTool(BaseTool):
    @classmethod
    def get_name(cls):
        return "📁 File Manager"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(QDir.currentPath()))
        self.tree.setColumnWidth(0, 350)
        
        layout.addWidget(QLabel("Global Host File System:"))
        layout.addWidget(self.tree)