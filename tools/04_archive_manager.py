from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QFileDialog
from core.base_tool import BaseTool

class ArchiveManagerTool(BaseTool):
    @classmethod
    def get_name(cls):
        return "📦 Archive Ops"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        btn = QPushButton("Decompress Target Payload (.zip/.tar/.7z)")
        btn.clicked.connect(self.extract)
        layout.addWidget(btn)
        layout.addStretch()

    def extract(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Archive")
        if filepath and self.is_safe(filepath):
            print(f"Extraction initialized for {filepath}")