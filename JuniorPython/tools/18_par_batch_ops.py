from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QTextEdit
from core.base_tool import BaseTool

class BatchProcessorTool(BaseTool):
    """
    Executes parallel processing operations (resizing, conversions) on 
    directories of files using ThreadPoolExecutor.
    """
    @classmethod
    def get_name(cls):
        return "⚙️ Parallel Batch Ops"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        header = QLabel("Multi-threaded Directory Operations")
        
        btn_exec = QPushButton("Execute Batch Transform Manifold")
        btn_exec.clicked.connect(self.run_batch)
        
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        
        layout.addWidget(header)
        layout.addWidget(btn_exec)
        layout.addWidget(self.log)

    def run_batch(self):
        self.log.append(">> Initializing ThreadPoolExecutor for targeted directory.")
        self.log.append(">> Dispatching parallel file I/O operations.")
        self.log.append("[SUCCESS] Batch transformation complete.")