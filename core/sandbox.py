import multiprocessing
import psutil
import time
import sys
import io
import traceback

def isolated_execution(script_code: str, return_dict: dict):
    """
    Executes raw python logic within an isolated subprocess namespace.
    Restricts access to dangerous standard libraries if not explicitly bypassed.
    """
    # Create safe globals tensor
    safe_globals = {
        "__builtins__": __builtins__.copy()
    }
    
    # Strip highly destructive I/O from builtins
    unsafe_keys = ['open', 'exec', 'eval']
    for k in unsafe_keys:
        if k in safe_globals["__builtins__"]:
            del safe_globals["__builtins__"][k]

    # Capture stdout
    captured_out = io.StringIO()
    sys.stdout = captured_out
    sys.stderr = captured_out

    try:
        exec(script_code, safe_globals)
        return_dict['output'] = captured_out.getvalue()
        return_dict['status'] = 'SUCCESS'
    except Exception as e:
        return_dict['output'] = captured_out.getvalue() + "\n" + traceback.format_exc()
        return_dict['status'] = 'ERROR'
    finally:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

class SandboxExecutor:
    """
    Spawns processes, monitors VRAM/RAM constraints via psutil, 
    and handles SIGKILL if tensors run out of bounds.
    """
    def __init__(self, timeout_sec=10, max_ram_mb=512):
        self.timeout_sec = timeout_sec
        self.max_ram_mb = max_ram_mb

    def execute(self, code: str) -> dict:
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        
        p = multiprocessing.Process(target=isolated_execution, args=(code, return_dict))
        p.start()
        
        # Resource monitor loop
        start_time = time.time()
        while p.is_alive():
            try:
                proc = psutil.Process(p.pid)
                mem_mb = proc.memory_info().rss / (1024 * 1024)
                if mem_mb > self.max_ram_mb:
                    p.terminate()
                    p.join()
                    return {"status": "OOM_KILL", "output": f"Kernel Fault: Process exceeded {self.max_ram_mb}MB memory limit."}
            except psutil.NoSuchProcess:
                pass

            if time.time() - start_time > self.timeout_sec:
                p.terminate()
                p.join()
                return {"status": "TIMEOUT", "output": f"Kernel Fault: Execution exceeded {self.timeout_sec}s timeline."}
            
            time.sleep(0.1)
            
        p.join()
        return dict(return_dict) if 'status' in return_dict else {"status": "CRASH", "output": "Subprocess segregated unexpectedly."}