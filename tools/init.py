"""
Tools Registry Module
Provides namespace aggregation for dynamic importlib discovery in main.py.
"""
from typing import List

# This array acts as an explicit boot order if dependency chaining is required later.
# Currently, main.py dynamically loads *.py files, but this __all__ exposes them cleanly.
__all__: List[str] = [
    "01_file_manager",
    "02_scrubber",
    "03_downloader",
    "04_archive_manager",
    "05_video_editor",
    "06_automations",
    "07_ide_features",
    "08_llm_agent",
    "09_legal_assets_shield",
    "10_script_hunter",
    "11_data_manifold",
    "12_telemetry_hub",
    "13_env_manager"
]