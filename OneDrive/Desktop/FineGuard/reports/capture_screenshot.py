"""
FinGuard - Headless Chrome/Edge DevTools Protocol Screenshot Capture
Connects via CDP WebSocket to capture full rendered Streamlit DOM.
"""

import os
import sys
import time
import json
import base64
import subprocess
import urllib.request
import asyncio
import websockets

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CDP_PORT = 9222


async def capture_cdp_screenshot(url: str, output_path: str, wait_seconds: int = 4):
    # 1. Start Edge with remote debugging
    edge_cmd = [
        EDGE_PATH,
        "--headless=new",
        f"--remote-debugging-port={CDP_PORT}",
        "--window-size=1440,1080",
        "--hide-scrollbars",
        "--disable-gpu",
        "about:blank"
    ]
    edge_proc = subprocess.Popen(edge_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(1.5)

    try:
        # 2. Get active page target
        list_url = f"http://127.0.0.1:{CDP_PORT}/json/list"
        req = urllib.request.Request(list_url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            targets = json.loads(resp.read().decode())
        
        if not targets:
            raise RuntimeError("No targets found in CDP response.")
        
        ws_url = targets[0]["webSocketDebuggerUrl"]
        print(f"Connecting to CDP: {ws_url}")

        async with websockets.connect(ws_url, max_size=20*1024*1024) as ws:
            # Enable Page
            await ws.send(json.dumps({"id": 1, "method": "Page.enable"}))
            await ws.recv()

            # Navigate to Streamlit URL
            print(f"Navigating to {url}...")
            await ws.send(json.dumps({"id": 2, "method": "Page.navigate", "params": {"url": url}}))
            await ws.recv()

            # Wait for Streamlit React rendering and cache retrieval
            print(f"Waiting {wait_seconds}s for Streamlit DOM & Plotly charts to mount...")
            await asyncio.sleep(wait_seconds)

            # Capture Screenshot
            print("Capturing rendered screenshot...")
            await ws.send(json.dumps({"id": 3, "method": "Page.captureScreenshot", "params": {"format": "png"}}))
            
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                if data.get("id") == 3:
                    img_data = base64.b64decode(data["result"]["data"])
                    with open(output_path, "wb") as f:
                        f.write(img_data)
                    print(f"Saved rendered screenshot to: {output_path} ({len(img_data)} bytes)")
                    break

    finally:
        edge_proc.terminate()
        try:
            edge_proc.wait(timeout=2)
        except Exception:
            edge_proc.kill()


if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8501"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "reports/rendered_overview.png"
    asyncio.run(capture_cdp_screenshot(target_url, out_file))

