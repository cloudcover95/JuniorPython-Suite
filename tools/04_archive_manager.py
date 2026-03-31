from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QFileDialog
from core.base_tool import BaseTool
import zipfile

class ArchiveManagerTool(BaseTool):
    @classmethod
    def get_name(cls):
        return "Archive Protocol"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        btn = QPushButton("Decompress Target Payload (.zip)")
        btn.clicked.connect(self.extract)
        layout.addWidget(btn)
        layout.addStretch()

    def extract(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Archive", filter="Zip files (*.zip)")
        if filepath:
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(filepath.replace('.zip', '_extracted'))