import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout
from core.base_tool import BaseTool

class WorkspaceAuditTool(BaseTool):
    """
    Cryptographic snapshot ledger for generic workspace integrity.
    Allows users to track structural drift in their local projects.
    """
    @classmethod
    def get_name(cls):
        return "🗄️ Workspace Audit"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        header = QLabel("Local Directory Integrity Ledger (JSON)")
        header.setStyleSheet("color: #00ff41; font-weight: bold;")
        
        btn_bar = QHBoxLayout()
        btn_audit = QPushButton("Snapshot Current Topology")
        btn_audit.clicked.connect(self.run_audit)
        
        btn_load = QPushButton("Verify Matrix Integrity")
        btn_load.clicked.connect(self.verify_ledger)
        
        btn_bar.addWidget(btn_audit)
        btn_bar.addWidget(btn_load)
        
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background-color: #0c0c0c; color: #d4d4d4;")
        
        layout.addWidget(header)
        layout.addLayout(btn_bar)
        layout.addWidget(self.log)

        self.ledger_path = Path("workspace_ledger.json")

    def _hash_file(self, filepath):
        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                hasher.update(f.read())
            return hasher.hexdigest()
        except Exception:
            return None

    def run_audit(self):
        self.log.append(">> Mapping current directory topology...")
        snapshot = {"timestamp": datetime.now().isoformat(), "modules": {}}
        
        target_dir = self.app_context.tools_dir.parent
        for root, _, files in os.walk(target_dir):
            if any(f in root for f in ["01_Legal", "02_Assets", "__pycache__", ".git"]):
                continue
            for file in files:
                fpath = Path(root) / file
                snapshot["modules"][str(fpath)] = self._hash_file(fpath)

        with open(self.ledger_path, 'w') as f:
            json.dump(snapshot, f, indent=4)
        self.log.append(f">> Snapshot committed. Recorded {len(snapshot['modules'])} vectors.")

    def verify_ledger(self):
        if not self.ledger_path.exists():
            self.log.append("[FAULT] No ledger found. Run snapshot first.")
            return
        with open(self.ledger_path, 'r') as f:
            ledger = json.load(f)
            
        discrepancies = 0
        for fpath_str, expected_hash in ledger["modules"].items():
            if self._hash_file(Path(fpath_str)) != expected_hash:
                self.log.append(f"[WARN] Structural drift detected: {fpath_str}")
                discrepancies += 1
                
        if discrepancies == 0:
            self.log.append("<b style='color:#00ff00;'>>> Integrity Verified. Geometry is rigid.</b>")