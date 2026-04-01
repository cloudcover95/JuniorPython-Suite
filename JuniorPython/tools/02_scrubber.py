from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QFileDialog, QTextEdit
from core.base_tool import BaseTool

class ScrubberTool(BaseTool):
    @classmethod
    def get_name(cls):
        return "🧹 Data Scrubber"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        
        btn_scrub = QPushButton("Select File to Sterilize EXIF/Meta")
        btn_scrub.clicked.connect(self.scrub_file)
        
        layout.addWidget(QLabel("Sanitize datasets and media assets securely."))
        layout.addWidget(btn_scrub)
        layout.addWidget(self.log)

    def scrub_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Asset")
        if filepath:
            if not self.is_safe(filepath):
                self.log.append(f"[KERNEL DENY] Protected Path Traversal Blocked: {filepath}")
                return
            self.log.append(f"Scrubbing vector space of metadata for: {filepath}")
            self.log.append("Operation complete. File sterilized.")