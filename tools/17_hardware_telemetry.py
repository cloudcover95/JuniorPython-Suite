from PySide6.QtWidgets import QVBoxLayout, QLabel, QProgressBar, QHBoxLayout
from PySide6.QtCore import QTimer
from core.base_tool import BaseTool
import psutil

class HWTelemetryTool(BaseTool):
    """
    Cross-platform hardware polling. Maps local system constraints (CPU/RAM).
    """
    @classmethod
    def get_name(cls):
        return "💻 Hardware Telemetry"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        header = QLabel("Local Node Resource Utilization")
        header.setStyleSheet("color: #ffd166; font-weight: bold;")
        
        # CPU
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel("Global CPU Tensor:"))
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        cpu_layout.addWidget(self.cpu_bar)
        
        # RAM
        ram_layout = QHBoxLayout()
        ram_layout.addWidget(QLabel("Memory Allocation:"))
        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)
        ram_layout.addWidget(self.ram_bar)
        
        layout.addWidget(header)
        layout.addLayout(cpu_layout)
        layout.addLayout(ram_layout)
        layout.addStretch()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_hardware)
        self.timer.start(1000)

    def poll_hardware(self):
        self.cpu_bar.setValue(int(psutil.cpu_percent()))
        self.ram_bar.setValue(int(psutil.virtual_memory().percent))