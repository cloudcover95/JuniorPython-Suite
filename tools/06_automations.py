from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton
from core.base_tool import BaseTool

class AutomationsTool(BaseTool):
    @classmethod
    def get_name(cls):
        return "Local Automations"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Cron / APScheduler Daemon Management"))
        btn1 = QPushButton("Run Asset Directory Cleanup")
        btn2 = QPushButton("Execute Nightly DB Snapshot")
        layout.addWidget(btn1)
        layout.addWidget(btn2)
        layout.addStretch()