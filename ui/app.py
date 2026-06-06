# path: ui/app.py

"""
JuniorPython UI (FastAPI + templates)

Modern workflow management UI inspired by JuniorHome.
"""

from fastapi import FastAPI, Request

from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates

import uvicorn

from src.workflow_engine import WorkflowEngine

from src.bitnet_runner import BitNetRunner


app = FastAPI(title="JuniorPython - BitNet Workflows")

templates = Jinja2Templates(directory="ui/templates")

bitnet = BitNetRunner(bitnet_version="1.58")
engine = WorkflowEngine(bitnet_runner=bitnet)


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "state": engine.get_ui_state()
    })


@app.post("/run_example")
def run_example():
    engine.add_step("load", lambda x: {"data": "real"})
    engine.add_step("bitnet_infer", lambda x: bitnet.run_inference(x))
    results = engine.run_workflow({"start": True})
    return {"results": results}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
