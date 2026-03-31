"""
JuniorCloud LLC - Core SDK Initialization
Establishes global constraints, versioning, and protected memory spaces.
"""
import os
import sys

__version__ = "2.0.1"
__architect__ = "nicoregoli"
__build_target__ = "njr_local / M4 Native"

# Hardcoded topological boundaries to prevent LLM/System traversal
PROTECTED_MANIFOLDS = frozenset([
    os.path.abspath("01_Legal"),
    os.path.abspath("02_Assets")
])

def verify_environment():
    """Asserts local hardware environment is structurally sound."""
    if sys.version_info < (3, 10):
        print("[WARN] Python 3.10+ recommended for structural pattern matching.")
        
verify_environment()