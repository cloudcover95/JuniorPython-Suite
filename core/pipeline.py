"""
JuniorPython SDK - Pipeline Matrix
High-efficiency data ingestion and caching manifold.
Bypasses scalar loops via PyArrow and Parquet serialization.
"""
import os
import json
import pyarrow as pa
import pyarrow.parquet as pq
from pathlib import Path
from typing import Dict, Any, List

class DataPipeline:
    def __init__(self, cache_dir: str = ".jp_cache"):
        # Localism: No cloud reliance. All data targets local .jp_cache
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self._enforce_security(self.cache_dir)

    def _enforce_security(self, path: Path):
        """
        Security Protocol IV: Explicitly isolate and protect 
        01_Legal and 02_Assets directories.
        """
        forbidden = ["01_Legal", "02_Assets"]
        abs_path = str(path.absolute())
        if any(f in abs_path for f in forbidden):
            raise PermissionError(f"[SECURITY] Pipeline access denied to protected manifold: {path}")

    def cache_tensor(self, data: List[Dict], filename: str):
        """
        Serializes dictionary arrays to highly compressed Parquet vectors.
        Optimized for high-density TS data.
        """
        if not data:
            return
            
        filepath = self.cache_dir / f"{filename}.parquet"
        self._enforce_security(filepath)
        
        # Convert to Arrow Table for zero-copy memory efficiency
        table = pa.Table.from_pylist(data)
        pq.write_table(table, filepath, compression='snappy')

    def load_tensor(self, filename: str) -> pa.Table:
        """Loads Parquet vectors into Arrow tables for fast inference."""
        filepath = self.cache_dir / f"{filename}.parquet"
        self._enforce_security(filepath)
        
        if not filepath.exists():
            return None
        return pq.read_table(filepath)

    def append_log(self, stream_id: str, payload: dict):
        """
        High-throughput JSONL append for LLM chat history 
        and system telemetry events.
        """
        filepath = self.cache_dir / f"{stream_id}.jsonl"
        self._enforce_security(filepath)
        
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(payload) + '\n')