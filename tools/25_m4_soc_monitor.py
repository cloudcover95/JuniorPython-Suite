from PySide6.QtWidgets import QVBoxLayout, QLabel, QProgressBar, QHBoxLayout
from PySide6.QtCore import QTimer
from core.base_tool import BaseTool
import psutil

class M4SoCMonitorTool(BaseTool):
    """
    Darwin-specific hardware polling for the M4 Unified Memory architecture.
    """
    @classmethod
    def get_name(cls):
        return "💻 M4 SoC Monitor"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        header = QLabel("Apple Silicon M4 (16GB) Unified Memory State")
        header.setStyleSheet("color: #a8dadc; font-weight: bold;")
        
        mem_layout = QHBoxLayout()
        mem_layout.addWidget(QLabel("Unified Memory Paging:"))
        self.mem_bar = QProgressBar()
        self.mem_bar.setRange(0, 100)
        mem_layout.addWidget(self.mem_bar)
        
        layout.addWidget(header)
        layout.addLayout(mem_layout)
        layout.addStretch()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_hardware)
        self.timer.start(2000)

    def poll_hardware(self):
        # Native psutil mapping to Darwin vm_stat
        mem = psutil.virtual_memory()
        self.mem_bar.setValue(int(mem.percent))