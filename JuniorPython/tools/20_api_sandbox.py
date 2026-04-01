from PySide6.QtWidgets import QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QTextEdit, QHBoxLayout
from core.base_tool import BaseTool

class APISandboxTool(BaseTool):
    """
    Local REST API execution utility for testing proprietary Flask/FastAPI logic.
    """
    @classmethod
    def get_name(cls):
        return "🧪 Local API Sandbox"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        header = QLabel("REST Endpoint / Payload Testing")
        header.setStyleSheet("color: #118ab2; font-weight: bold;")
        
        bar = QHBoxLayout()
        self.method = QComboBox()
        self.method.addItems(["GET", "POST", "PUT", "DELETE"])
        self.endpoint = QLineEdit()
        self.endpoint.setPlaceholderText("http://localhost:5000/api/v1/...")
        
        btn_send = QPushButton("Transmit Payload")
        btn_send.clicked.connect(self.send_request)
        
        bar.addWidget(self.method)
        bar.addWidget(self.endpoint)
        bar.addWidget(btn_send)
        
        self.payload_box = QTextEdit()
        self.payload_box.setPlaceholderText('{"key": "value"} (JSON Payload)')
        self.payload_box.setMaximumHeight(100)
        
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        
        layout.addWidget(header)
        layout.addLayout(bar)
        layout.addWidget(self.payload_box)
        layout.addWidget(self.log)

    def send_request(self):
        verb = self.method.currentText()
        url = self.endpoint.text()
        if not url: return
        self.log.append(f">> Constructing {verb} request to {url}")
        self.log.append(">> Awaiting Requests/Urllib3 matrix integration.")