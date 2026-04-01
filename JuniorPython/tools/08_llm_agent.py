from PySide6.QtWidgets import QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import QThread, Signal
from core.base_tool import BaseTool
import ollama
import os
import re

class AgentThread(QThread):
    response_ready = Signal(str)
    
    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt
        
    def run(self):
        try:
            res = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': self.prompt}])
            self.response_ready.emit(res['message']['content'])
        except Exception as e:
            self.response_ready.emit(f"[Kernel Error] Ollama bind failed: {str(e)}")

class LLMAgentTool(BaseTool):
    """
    Generative Intelligence Matrix.
    Capable of writing tools directly to /tools/ for immediate dynamic injection.
    """
    @classmethod
    def get_name(cls):
        return "Agentic Operator (Ollama)"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.chat_log = QTextEdit()
        self.chat_log.setReadOnly(True)
        
        input_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Command agent to build tool or analyze script...")
        self.user_input.returnPressed.connect(self.send_query)
        
        btn_send = QPushButton("Transmit")
        btn_send.clicked.connect(self.send_query)
        
        input_layout.addWidget(self.user_input)
        input_layout.addWidget(btn_send)
        
        layout.addWidget(self.chat_log)
        layout.addLayout(input_layout)

    def send_query(self):
        prompt = self.user_input.text()
        if not prompt: return
        self.chat_log.append(f"<b>User:</b> {prompt}")
        self.user_input.clear()
        
        system_prompt = (
            "You are PyForge AI. You can generate PySide6 tools. "
            "If requested to build a tool, output raw Python code enclosed in ```python\n...\n```. "
            f"User query: {prompt}"
        )
        
        self.thread = AgentThread(system_prompt)
        self.thread.response_ready.connect(self.handle_response)
        self.thread.start()

    def handle_response(self, text):
        self.chat_log.append(f"<b>Agent:</b> {text}")
        
        # Intercept generated code logic
        match = re.search(r'```python\n(.*?)```', text, re.DOTALL)
        if match:
            code = match.group(1)
            filepath = os.path.join(self.app_context.tools_dir, "09_generated_tool.py")
            with open(filepath, 'w') as f:
                f.write(code)
            self.chat_log.append("<i>[System] New module topology compiled. Triggering hot-reload.</i>")
            self.app_context.load_tools()