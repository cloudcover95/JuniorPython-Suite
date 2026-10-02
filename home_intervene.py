"""Read Home mesh. Does not pack a second trit. Does not send."""
from __future__ import annotations

import json
from pathlib import Path

MESH = Path.home() / ".juniorhome" / "gaia_mesh"


def read() -> dict:
    out = {"port": "JuniorPython-Suite", "send": False, "model_pull": False, "bind": "127.0.0.1"}
    for name in ("web3_mesh.jsonl", "wallet_class.jsonl", "ledger.jsonl"):
        path = MESH / name
        out[name] = path.exists()
    return out


if __name__ == "__main__":
    print(json.dumps(read(), indent=2))
