from PySide6.QtWidgets import (QVBoxLayout, QPushButton, QFileDialog, QTableWidget, 
                               QTableWidgetItem, QLabel, QHBoxLayout, QTextEdit)
from core.base_tool import BaseTool
import traceback

try:
    import pandas as pd
    import numpy as np
    NUMERIC_ACTIVE = True
except ImportError:
    NUMERIC_ACTIVE = False

class DataManifoldTool(BaseTool):
    """
    High-density .parquet ingestion and vectorized operations (SVD, covariance).
    Strictly avoids scalar loops.
    """
    @classmethod
    def get_name(cls):
        return "📊 Data Manifold (.parquet)"

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.header = QLabel("High-Frequency TS / Parquet Inspector")
        self.header.setStyleSheet("color: #007acc; font-weight: bold;")
        
        btn_bar = QHBoxLayout()
        btn_load = QPushButton("Ingest .parquet / .csv")
        btn_load.clicked.connect(self.load_data)
        
        btn_svd = QPushButton("Compute SVD Mesh ($A = U \\Sigma V^T$)")
        btn_svd.clicked.connect(self.compute_svd)
        btn_svd.setStyleSheet("background-color: #512da8;")
        
        btn_bar.addWidget(btn_load)
        btn_bar.addWidget(btn_svd)
        
        self.table = QTableWidget()
        self.table.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4; gridline-color: #333;")
        
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(150)
        
        layout.addWidget(self.header)
        layout.addLayout(btn_bar)
        layout.addWidget(self.table)
        layout.addWidget(self.log)
        
        self.df = None

    def load_data(self):
        if not NUMERIC_ACTIVE:
            self.log.append("[KERNEL FAULT] pandas/numpy missing. Run: pip install pandas numpy pyarrow")
            return
            
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Tensor Data", filter="Data (*.parquet *.csv)")
        if not filepath or not self.is_safe(filepath): return
        
        try:
            if filepath.endswith('.parquet'):
                self.df = pd.read_parquet(filepath)
            else:
                self.df = pd.read_csv(filepath)
                
            self.log.append(f">> Ingested Manifold: {filepath} | Shape: {self.df.shape}")
            self.render_table()
        except Exception as e:
            self.log.append(f"[ERROR] Ingestion failed: {str(e)}")

    def render_table(self):
        if self.df is None: return
        preview = self.df.head(100) # Limit render to 100 rows to prevent GUI thread lock
        self.table.setColumnCount(len(preview.columns))
        self.table.setRowCount(len(preview))
        self.table.setHorizontalHeaderLabels(preview.columns.astype(str))
        
        for i in range(len(preview)):
            for j in range(len(preview.columns)):
                val = str(preview.iloc[i, j])
                self.table.setItem(i, j, QTableWidgetItem(val))
        self.table.resizeColumnsToContents()

    def compute_svd(self):
        if self.df is None:
            self.log.append("[WARN] No tensor matrix loaded.")
            return
            
        # Filter for numeric columns to build matrix A
        numeric_df = self.df.select_dtypes(include=[np.number]).dropna()
        if numeric_df.empty:
            self.log.append("[WARN] Matrix lacks continuous numerical distributions.")
            return
            
        self.log.append(">> Executing SVD ($A = U \\Sigma V^T$) on numeric tensor...")
        try:
            A = numeric_df.to_numpy()
            # Vectorized SVD computation via LAPACK/BLAS
            U, s, VT = np.linalg.svd(A, full_matrices=False)
            
            self.log.append(f"<b>SVD Successful.</b>")
            self.log.append(f"Singular Values (\\Sigma) Top 5: {s[:5]}")
            self.log.append(f"Shape U: {U.shape}, Shape VT: {VT.shape}")
            
            # Feature Disagreement Score (FDS) stub logic could hook in here
        except np.linalg.LinAlgError as e:
            self.log.append(f"[KERNEL FAULT] SVD Convergence Failed: {traceback.format_exc()}")