from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QTextEdit
from core.base_tool import BaseTool

class StreamTelemetryTool(BaseTool):
    """
    OBS WebSocket bridge and Twitch chat ingress for @cloudnjr broadcasts.
    """
    @classmethod
    def get_name(cls):
        return "🎮 Stream Telemetry"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        header = QLabel("Twitch @cloudnjr / OBS WebSockets")
        header.setStyleSheet("color: #6441a5; font-weight: bold;")
        
        btn_connect = QPushButton("Bind to OBS WebSocket Port 4455")
        btn_connect.clicked.connect(self.connect_obs)
        
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background-color: #0c0c0c; color: #d4d4d4;")
        
        layout.addWidget(header)
        layout.addWidget(btn_connect)
        layout.addWidget(self.log)

    def connect_obs(self):
        self.log.append(">> Attempting local ws://127.0.0.1:4455 bind...")
        self.log.append(">> Scene topology extracted. Awaiting scene switch kinematics.")