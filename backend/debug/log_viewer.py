# log_viewer.py
import os
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn

LOG_FILE = os.path.abspath(os.path.join("..", "data", "logs", "app.log"))
app = FastAPI()

# Simple HTML page to display logs
html = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Logs</title>
    <style>
        body {
            font-family: monospace;
            background: #0f172a;
            color: #0f0;
            margin: 0;
            padding: 0;
        }

        h2 {
            margin: 0;
            padding: 15px;
            background: #1e293b;
            border-bottom: 1px solid #334155;
        }

        #logs {
            padding: 15px;
            height: 92vh;
            overflow-y: auto;
            white-space: pre-wrap;
            word-break: break-word;
        }

        .ERROR { color: #ef4444; }
        .INFO { color: #22c55e; }
        .WARNING { color: #facc15; }
        .DEBUG { color: #38bdf8; }

        .log-line {
            margin-bottom: 6px;
        }
    </style>
</head>
<body>
    <h2>Live Log Viewer</h2>
    <div id="logs"></div>

    <script>
        const logsDiv = document.getElementById("logs");
        const ws = new WebSocket("ws://localhost:8001/logs");
        ws.onmessage = (event) => {
            const line = event.data;

            const div = document.createElement("div");
            div.classList.add("log-line");

            if (line.includes("ERROR")) div.classList.add("ERROR");
            else if (line.includes("INFO")) div.classList.add("INFO");
            else if (line.includes("WARNING")) div.classList.add("WARNING");
            else if (line.includes("DEBUG")) div.classList.add("DEBUG");

            div.textContent = line;
            logsDiv.appendChild(div);

            logsDiv.scrollTop = logsDiv.scrollHeight;
        };
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

@app.websocket("/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    # Start at end of file
    with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if line:
                await websocket.send_text(line.rstrip())
            else:
                await asyncio.sleep(0.2)  # Poll every 200ms

if __name__ == "__main__":
    # Run FastAPI server
    uvicorn.run("log_viewer:app", host="localhost", port=8001, reload=True)