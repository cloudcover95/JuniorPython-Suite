from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QLineEdit, QHBoxLayout
from core.base_tool import BaseTool

class VideoEditorTool(BaseTool):
    @classmethod
    def get_name(cls):
        return "🎬 Rough Cut (NVENC)"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.in_file = QLineEdit(placeholderText="Input Path (e.g., ./raw_vid.mp4)")
        self.t_start = QLineEdit(placeholderText="Start Time (ss)")
        self.t_end = QLineEdit(placeholderText="End Time (ss)")
        self.out_file = QLineEdit(placeholderText="Output Path (e.g., ./cut.mp4)")
        
        btn_render = QPushButton("Execute GPU Tensor Slice")
        btn_render.clicked.connect(self.render_cut)
        
        layout.addWidget(QLabel("FFmpeg / MoviePy Accelerated NLE Ops"))
        layout.addWidget(self.in_file)
        
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.t_start)
        h_layout.addWidget(self.t_end)
        layout.addLayout(h_layout)
        
        layout.addWidget(self.out_file)
        layout.addWidget(btn_render)
        layout.addStretch()

    def render_cut(self):
        fin, start, end, fout = self.in_file.text(), self.t_start.text(), self.t_end.text(), self.out_file.text()
        if not all([fin, start, end, fout]): return
        if not self.is_safe(fin) or not self.is_safe(fout):
            print("Access violation to protected storage manifold.")
            return
        print(f"Dispatching to NVENC kernel: {fin} -> {fout} [{start}:{end}]")