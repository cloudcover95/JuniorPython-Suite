JuniorPython Suite Modular Python IDE & Edge-Compute SDKJuniorPython is a logic-dense, power-efficient development suite engineered for local-first execution on Apple Silicon (M4/M1) and Windows 11 (CUDA) environments. It operates as a sovereign manifold, bypassing cloud reliance for LLM inference, data processing, and automation.Core ArchitectureDynamic Plugin System: Tools are isolated .py scripts located in /tools/, hot-reloaded via importlib.Data Pipeline: High-throughput ingestion using Snappy-compressed .parquet vectors for zero-copy memory access.Multiprocess Sandbox: Isolated execution kernel for safe script testing with hardware resource monitoring (RAM/CPU).Security Protocol IV: Explicit path isolation for 01_Legal and 02_Assets to prevent agent traversal or indexing.Deployment ProtocolInitialize Hardware: Ensure Ollama is running locally for neural inference.Provision Environment:pip install -r requirements.txt
ollama pull llama3.2:3b
Execute Matrix:python main.py
Repository Topologycore/: System kernels (Sandbox, Pipeline, BaseTool).tools/: Extensible tool manifold (Branches 01-27)..jp_cache/: Localized Parquet/JSONL data vault.

PyForge SuiteModular Python IDE and Automation Powerhouse for Windows 11.Engineered for CUDA-accelerated video rough cuts and local LLM agentic workflows.Deployment ProtocolInitialize environment:python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
Ensure Ollama is running locally:ollama serve
ollama pull llama3.2
Execute core runtime:python main.py
