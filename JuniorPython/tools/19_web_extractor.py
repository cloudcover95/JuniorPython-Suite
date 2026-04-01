from PySide6.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QHBoxLayout
from core.base_tool import BaseTool

class WebExtractorTool(BaseTool):
    """
    Generic DOM/HTML scraping utility. Safely fetches external vectors.
    """
    @classmethod
    def get_name(cls):
        return "🕸️ Web Extractor"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        header = QLabel("Targeted DOM / API Payload Extraction")
        header.setStyleSheet("color: #ef476f; font-weight: bold;")
        
        bar = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://...")
        btn_fetch = QPushButton("Fetch Vector")
        btn_fetch.clicked.connect(self.fetch_url)
        
        bar.addWidget(self.url_input)
        bar.addWidget(btn_fetch)
        
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        
        layout.addWidget(header)
        layout.addLayout(bar)
        layout.addWidget(self.log)

    def fetch_url(self):
        target = self.url_input.text()
        if not target: return
        self.log.append(f">> Sending HTTP GET request to: {target}")
        self.log.append(">> Awaiting BeautifulSoup HTML/XML parsing logic.")