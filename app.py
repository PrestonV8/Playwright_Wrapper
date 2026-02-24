from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import os
import subprocess
import threading
from datetime import datetime

app = FastAPI()

# simple in-memory run tracking (MVP)
RUNS = {}

def run_job(run_id: str, env: str, suite: str):
    RUNS[run_id]["status"] = "RUNNING"

    cmd = f'python run_playwright.py --env {env} --suite "{suite}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    RUNS[run_id]["stdout"] = result.stdout
    RUNS[run_id]["stderr"] = result.stderr
    RUNS[run_id]["exit code"] = result.returncode
    RUNS[run_id]["status"] = "PASSED" if result.returncode ==0 else "FAILED"



@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Playwright Runner</title>
        <style>
          :root{
            --bg1:#0ea5e9;
            --bg2:#8b5cf6;
            --panel:#0b1220;
            --card: rgba(255,255,255,.10);
            --cardBorder: rgba(255,255,255,.18);
            --text:#e8eefc;
            --muted: rgba(232,238,252,.75);
            --shadow: 0 20px 60px rgba(0,0,0,.35);
            --radius: 18px;
            --success:#22c55e;
            --fail:#ef4444;
            --warn:#f59e0b;
          }
          *{ box-sizing:border-box; }
          body{
            margin:0;
            font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial, "Noto Sans", "Apple Color Emoji","Segoe UI Emoji";
            color: var(--text);
            min-height:100vh;
            background: radial-gradient(1200px 600px at 20% 10%, rgba(255,255,255,.18), transparent 55%),
                        radial-gradient(900px 500px at 90% 30%, rgba(255,255,255,.14), transparent 55%),
                        linear-gradient(135deg, var(--bg1), var(--bg2));
          }
          .wrap{
            max-width: 1000px;
            margin: 0 auto;
            padding: 36px 20px 60px;
          }
          .topbar{
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:16px;
            margin-bottom: 22px;
          }
          .brand{
            display:flex;
            align-items:center;
            gap:14px;
          }
          .logo{
            width:46px;height:46px;border-radius:14px;
            background: rgba(255,255,255,.16);
            border: 1px solid var(--cardBorder);
            display:grid;place-items:center;
            box-shadow: var(--shadow);
          }
          .logo span{
            font-size:22px;
            font-weight:900;
            letter-spacing:.5px;
          }
          h1{
            margin:0;
            font-size: 30px;
            line-height: 1.1;
            letter-spacing: .2px;
          }
          .subtitle{
            margin:6px 0 0;
            color: var(--muted);
            font-size: 14px;
          }

          .grid{
            display:grid;
            grid-template-columns: 1.2fr .8fr;
            gap: 18px;
            margin-top: 18px;
          }
          @media (max-width: 900px){
            .grid{ grid-template-columns: 1fr; }
          }

          .card{
            background: var(--card);
            border: 1px solid var(--cardBorder);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 18px;
            backdrop-filter: blur(10px);
          }
          .card h2{
            margin: 0 0 12px;
            font-size: 18px;
            letter-spacing: .2px;
          }
          .row{
            display:flex;
            gap: 12px;
            flex-wrap: wrap;
            align-items:end;
          }
          label{
            display:block;
            font-size: 12px;
            color: var(--muted);
            margin: 0 0 8px;
          }
          select, input{
            width: 100%;
            padding: 12px 12px;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,.22);
            background: rgba(10,14,25,.35);
            color: var(--text);
            outline: none;
            font-size: 15px;
          }
          select:focus, input:focus{
            border-color: rgba(255,255,255,.42);
            box-shadow: 0 0 0 4px rgba(255,255,255,.10);
          }
          .field{ flex: 1; min-width: 220px; }
          .field.small{ flex: .7; min-width: 200px; }
          .btn{
            padding: 12px 14px;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,.20);
            background: linear-gradient(135deg, rgba(34,197,94,.95), rgba(14,165,233,.95));
            color: #071019;
            font-weight: 900;
            font-size: 15px;
            cursor:pointer;
            transition: transform .06s ease, filter .2s ease;
            min-width: 160px;
          }
          .btn:hover{ filter: brightness(1.05); }
          .btn:active{ transform: translateY(1px); }
          .btn:disabled{
            opacity:.6;
            cursor:not-allowed;
            filter: grayscale(.2);
          }

          .kpis{
            display:grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
          }
          .kpi{
            padding: 14px;
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,.18);
            background: rgba(10,14,25,.28);
          }
          .kpi .label{ font-size: 12px; color: var(--muted); margin-bottom: 6px; }
          .kpi .value{ font-size: 20px; font-weight: 900; }

          .panel{
            background: rgba(10,14,25,.45);
            border: 1px solid rgba(255,255,255,.18);
            border-radius: 16px;
            padding: 14px;
            margin-top: 14px;
          }
          pre{
            margin:0;
            color: #d7e2ff;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            white-space: pre-wrap;
            word-break: break-word;
            font-size: 13px;
            line-height: 1.5;
          }
          .hint{
            margin-top: 10px;
            color: rgba(232,238,252,.72);
            font-size: 13px;
          }
          .badge{
            display:inline-flex;
            align-items:center;
            gap:8px;
            padding: 8px 10px;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,.20);
            background: rgba(10,14,25,.30);
            color: rgba(232,238,252,.88);
            font-size: 12px;
          }
          .dot{
            width:10px;height:10px;border-radius:99px;
            background: var(--warn);
            box-shadow: 0 0 0 4px rgba(245,158,11,.18);
          }
          .footer{
            margin-top: 18px;
            font-size: 12px;
            color: rgba(232,238,252,.70);
          }
          a{ color: rgba(232,238,252,.95); }
        </style>
      </head>
      <body>
        <div class="wrap">

          <div class="topbar">
            <div class="brand">
              <div class="logo"><span>PW</span></div>
              <div>
                <h1>Playwright Runner</h1>
                <div class="subtitle">Launch suites fast • Track logs live • Keep it simple</div>
              </div>
            </div>
            <div class="badge" title="This is a local UI for triggering your wrapper runs">
              <span class="dot"></span>
              <span>Ready to run</span>
            </div>
          </div>

          <div class="grid">
            <div class="card">
              <h2>Start a run</h2>

              <div class="row">
                <div class="field small">
                  <label for="env">Environment</label>
                  <select id="env">
                    <option value="staging" selected>staging</option>
                    <option value="qa">qa</option>
                    <option value="prod">prod</option>
                  </select>
                </div>

                <div class="field">
                  <label for="suite">Suite</label>
                  <input id="suite" value="smoke" placeholder="e.g. smoke, regression, checkout" />
                </div>

                <button class="btn" id="runBtn" onclick="startRun()">Run suite →</button>
              </div>

              <div class="panel" style="margin-top:16px;">
                <pre id="out">Tip: choose an env, type a suite name, then click “Run suite”.</pre>
              </div>

              <div class="hint">After starting, you’ll be redirected to a live status page that refreshes every second.</div>
            </div>

            <div class="card">
              <h2>Quick info</h2>
              <div class="kpis">
                <div class="kpi">
                  <div class="label">Default suite</div>
                  <div class="value">smoke</div>
                </div>
                <div class="kpi">
                  <div class="label">Refresh rate</div>
                  <div class="value">1s</div>
                </div>
                <div class="kpi">
                  <div class="label">Run command</div>
                  <div class="value" style="font-size:12px; font-weight:700;">python run_playwright.py</div>
                </div>
                <div class="kpi">
                  <div class="label">UI endpoint</div>
                  <div class="value" style="font-size:12px; font-weight:700;">/ui/runs/&lt;id&gt;</div>
                </div>
              </div>

              <div class="footer">
                Next step: commit this UI change and push to GitHub — perfect for testing your CI workflow.
              </div>
            </div>
          </div>

        </div>

        <script>
          function setOutput(txt){
            document.getElementById("out").textContent = txt;
          }

          async function startRun() {
            const env = document.getElementById("env").value;
            const suite = document.getElementById("suite").value;

            const btn = document.getElementById("runBtn");
            btn.disabled = true;
            btn.textContent = "Starting…";

            setOutput("Starting run...");

            try {
              const res = await fetch("/runs", {
                method: "POST",
                headers: {"Content-Type":"application/json"},
                body: JSON.stringify({ env, suite })
              });

              const data = await res.json();
              setOutput("Run started!\\nrun_id=" + data.run_id + "\\nRedirecting to live status…");

              window.location.href = "/ui/runs/" + data.run_id;
            } catch (e) {
              setOutput("Error starting run:\\n" + (e?.message || e));
              btn.disabled = false;
              btn.textContent = "Run suite →";
            }
          }
        </script>
      </body>
    </html>
    """




@app.post("/runs")
def create_run(payload: dict):
    env = payload.get("env", "staging")
    suite = payload.get("suite", "smoke")

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = f"reports/{env}/{run_id}"

    RUNS[run_id] = {"status": "QUEUED", 
                    "env": env, 
                    "suite": suite,
                    "report_dir": report_dir}

    t = threading.Thread(target=run_job, args=(run_id, env, suite), daemon=True)
    t.start()

    return {"run_id": run_id, "status": "QUEUED", "env": env, "suite": suite}


@app.get("/runs/{run_id}")
def get_run(run_id: str):
    if run_id not in RUNS:
        return JSONResponse({"error": "run_id not found"}, status_code=404)
    return RUNS[run_id]



@app.get("/ui/runs/{run_id}", response_class=HTMLResponse)
def run_details_ui(run_id: str):
    return f"""
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Run {run_id}</title>

        <style>
          :root {{
            --bg1:#0ea5e9;
            --bg2:#8b5cf6;
            --card: rgba(255,255,255,.10);
            --cardBorder: rgba(255,255,255,.18);
            --text:#e8eefc;
            --muted: rgba(232,238,252,.75);
            --shadow: 0 20px 60px rgba(0,0,0,.35);
            --radius: 18px;
            --success:#22c55e;
            --fail:#ef4444;
            --warn:#f59e0b;
          }}

          * {{ box-sizing:border-box; }}

          body {{
            margin:0;
            font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;
            color: var(--text);
            min-height:100vh;
            background:
              radial-gradient(1200px 600px at 20% 10%, rgba(255,255,255,.18), transparent 55%),
              radial-gradient(900px 500px at 90% 30%, rgba(255,255,255,.14), transparent 55%),
              linear-gradient(135deg, var(--bg1), var(--bg2));
          }}

          .wrap {{
            max-width: 1100px;
            margin: 0 auto;
            padding: 28px 20px 60px;
          }}

          .card {{
            background: var(--card);
            border: 1px solid var(--cardBorder);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 18px;
            backdrop-filter: blur(10px);
          }}

          .top {{
            display:flex;
            align-items:flex-start;
            justify-content:space-between;
            gap:14px;
            flex-wrap:wrap;
            margin-bottom: 14px;
          }}

          h1 {{
            margin:0;
            font-size: 26px;
            letter-spacing:.2px;
          }}

          .sub {{
            margin-top: 6px;
            color: var(--muted);
            font-size: 13px;
          }}

          .pill {{
            display:inline-flex;
            align-items:center;
            gap:10px;
            padding: 10px 12px;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,.20);
            background: rgba(10,14,25,.30);
            font-size: 13px;
            font-weight: 800;
          }}

          .dot {{
            width:10px;
            height:10px;
            border-radius:999px;
            background: var(--warn);
            box-shadow: 0 0 0 4px rgba(245,158,11,.18);
          }}

          .meta {{
            display:grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            margin-top: 14px;
          }}

          @media (max-width: 900px) {{
            .meta {{ grid-template-columns: 1fr; }}
          }}

          .m {{
            padding: 14px;
            border-radius: 16px;
            border: 1px solid rgba(255,255,255,.18);
            background: rgba(10,14,25,.28);
          }}

          .m .k {{
            font-size:12px;
            color: var(--muted);
            margin-bottom: 6px;
          }}

          .m .v {{
            font-size:14px;
            font-weight: 800;
            word-break: break-word;
          }}

          .actions {{
            display:flex;
            gap:10px;
            flex-wrap:wrap;
            margin-top: 14px;
          }}

          .btn {{
            padding: 10px 12px;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,.20);
            background: rgba(10,14,25,.30);
            color: var(--text);
            font-weight: 800;
            cursor:pointer;
          }}

          .btn:hover {{ filter: brightness(1.06); }}

          .log {{
            margin-top: 14px;
            background: rgba(10,14,25,.55);
            border: 1px solid rgba(255,255,255,.18);
            border-radius: 16px;
            padding: 14px;
          }}

          pre {{
            margin:0;
            color:#d7e2ff;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            white-space: pre-wrap;
            word-break: break-word;
            font-size: 13px;
            line-height: 1.5;
          }}

          a {{
            color: rgba(232,238,252,.95);
          }}
        </style>
      </head>

      <body>
        <div class="wrap">
          <div class="card">
            <div class="top">
              <div>
                <h1>Run details</h1>
                <div class="sub">Live status & logs (auto-refresh every 1 second)</div>
              </div>

              <div class="pill" id="statusPill">
                <span class="dot" id="statusDot"></span>
                <span id="status">Loading...</span>
              </div>
            </div>

            <div class="meta">
              <div class="m">
                <div class="k">Run ID</div>
                <div class="v">{run_id}</div>
              </div>
              <div class="m">
                <div class="k">Run JSON</div>
                <div class="v"><a href="/runs/{run_id}">/runs/{run_id}</a></div>
              </div>
              <div class="m">
                <div class="k">Back</div>
                <div class="v"><a href="/">Home</a></div>
              </div>
            </div>

            <div class="actions">
              <button class="btn" onclick="refreshNow()">Refresh now</button>
              <button class="btn" onclick="copyRunId()">Copy run_id</button>
            </div>

            <div class="log">
              <pre id="logs">Loading logs...</pre>
            </div>
          </div>
        </div>

        <script>
          function setStatusUI(statusText) {{
            const statusUpper = (statusText || "").toUpperCase();

            let glow = "rgba(245,158,11,.18)";
            let dotColor = getComputedStyle(document.documentElement).getPropertyValue("--warn");

            if (statusUpper === "PASSED") {{
              glow = "rgba(34,197,94,.18)";
              dotColor = getComputedStyle(document.documentElement).getPropertyValue("--success");
            }} else if (statusUpper === "FAILED") {{
              glow = "rgba(239,68,68,.18)";
              dotColor = getComputedStyle(document.documentElement).getPropertyValue("--fail");
            }}

            const dot = document.getElementById("statusDot");
            dot.style.background = dotColor;
            dot.style.boxShadow = "0 0 0 4px " + glow;

            document.getElementById("status").textContent = statusText || "UNKNOWN";
          }}

          function copyRunId() {{
            navigator.clipboard.writeText("{run_id}");
          }}

          async function refreshNow() {{
            const res = await fetch("/runs/{run_id}");
            if (res.status === 404) {{
              setStatusUI("Waiting to register...");
              document.getElementById("logs").textContent =
                "This run hasn't shown up yet. If you just clicked Run, give it a moment.";
              return;
            }}

            const data = await res.json();
            setStatusUI(data.status);

            const out = ((data.stdout || "") + "\\n" + (data.stderr || "")).trim();
            document.getElementById("logs").textContent = out || "(no logs yet)";
          }}

          refreshNow();
          setInterval(refreshNow, 1000);
        </script>
      </body>
    </html>
    """


from fastapi.staticfiles import StaticFiles

# Serve the reports folder at /reports/
app.mount("/reports", StaticFiles(directory="reports"), name="reports")