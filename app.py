from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from run_playwright import run_tests

app = FastAPI()

# Ensure reports folder exists
Path("reports").mkdir(exist_ok=True)

# Serve report folder
app.mount("/reports", StaticFiles(directory="reports"), name="reports")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/run")
def run():
    log_file, exit_code = run_tests()
    return RedirectResponse(url=f"/reports/{log_file}", status_code=303)