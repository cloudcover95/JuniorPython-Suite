from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout
from PySide6.QtCore import QTimer
from core.base_tool import BaseTool
import psutil
import json
import asyncio
import threading
import websockets

class TelemetryHubTool(BaseTool):
    """
    WebSocket server binding to 0.0.0.0 for Slate AX local network transmission.
    Designed for iPad M1 Audit API dashboards.
    """
    @classmethod
    def get_name(cls):
        return "📡 Telemetry Hub (WS)"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.status_lbl = QLabel("WS SERVER: OFFLINE")
        self.status_lbl.setStyleSheet("color: #ff3b3b; font-weight: bold; font-size: 14px;")
        
        btn_bar = QHBoxLayout()
        self.btn_start = QPushButton("Init WebSocket Daemon (Port 8765)")
        self.btn_start.clicked.connect(self.start_server)
        
        btn_bar.addWidget(self.btn_start)
        
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background-color: #0d0d0d; color: #00ff41; font-family: Consolas;")
        
        layout.addWidget(QLabel("Live Hardware/Node Telemetry Broadcasts to iPad M1"))
        layout.addWidget(self.status_lbl)
        layout.addLayout(btn_bar)
        layout.addWidget(self.log)
        
        self.server_thread = None
        self.loop = None
        self.clients = set()
        
        # Hardware polling timer
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.broadcast_telemetry)

    def start_server(self):
        if self.server_thread and self.server_thread.is_alive():
            return
            
        self.btn_start.setEnabled(False)
        self.status_lbl.setText("WS SERVER: BINDING TO 0.0.0.0:8765")
        self.status_lbl.setStyleSheet("color: #ffff00; font-weight: bold; font-size: 14px;")
        
        self.server_thread = threading.Thread(target=self._run_asyncio_loop, daemon=True)
        self.server_thread.start()
        
        self.poll_timer.start(1000) # Poll hardware every 1s

    def _run_asyncio_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        start_server = websockets.serve(self._ws_handler, "0.0.0.0", 8765)
        
        self.loop.run_until_complete(start_server)
        # Update GUI from thread requires signals in strict prod, but log append is thread-safe enough in PySide6 for raw text
        self.log.append(">> Matrix active. Awaiting client connections on ws://<host_ip>:8765")
        
        self.status_lbl.setText("WS SERVER: ONLINE (0.0.0.0:8765)")
        self.status_lbl.setStyleSheet("color: #00ff00; font-weight: bold; font-size: 14px;")
        
        self.loop.run_forever()

    async def _ws_handler(self, websocket, path):
        self.clients.add(websocket)
        self.log.append(f">> [CONNECT] Audit node established: {websocket.remote_address}")
        try:
            async for message in websocket:
                # Handle incoming commands from iPad if necessary
                self.log.append(f"[IPAD INGRESS] {message}")
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.remove(websocket)
            self.log.append(f">> [DISCONNECT] Node dropped: {websocket.remote_address}")

    def broadcast_telemetry(self):
        if not self.clients or not self.loop: return
        
        # Gather topological hardware limits
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        
        payload = json.dumps({
            "type": "telemetry",
            "device": "njr_local",
            "metrics": {"cpu_utilization": cpu, "ram_utilization": ram}
        })
        
        # Dispatch to all clients securely
        asyncio.run_coroutine_threadsafe(self._send_to_all(payload), self.loop)

    async def _send_to_all(self, payload):
        if self.clients:
            await asyncio.gather(*[client.send(payload) for client in self.clients])