"""שרת מקומי לאתר החדשות: מגיש את האתר, מריץ את הסוכן בכל יום ב-08:00 (שעון ישראל)
ומאפשר רענון ידני מהכפתור באתר.

הרצה:  python server.py      ואז לפתוח  http://localhost:8000
"""

import json
import sys
import threading
import time
import webbrowser
from datetime import datetime, timedelta
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

import agent

PORT = 8000
REFRESH_HOUR = 8
lock = threading.Lock()


def run_agent():
    # מונע שתי הרצות במקביל (כפתור + תזמון)
    with lock:
        return agent.build()


def next_run(now):
    target = now.replace(hour=REFRESH_HOUR, minute=0, second=0, microsecond=0)
    return target if target > now else target + timedelta(days=1)


def scheduler():
    while True:
        now = datetime.now(agent.ISRAEL)
        target = next_run(now)
        agent.log(f"הרענון האוטומטי הבא: {target:%d.%m.%Y %H:%M}")
        while datetime.now(agent.ISRAEL) < target:
            time.sleep(30)
        try:
            run_agent()
        except Exception as error:
            agent.log(f"⚠ הרענון האוטומטי נכשל: {error}")


def config_state():
    return {"use_claude": bool(agent.load_config().get("use_claude")),
            "key_available": bool(agent.get_api_key())}


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/config":
            self.send_json(config_state())
        else:
            super().do_GET()

    def do_POST(self):
        try:
            if self.path == "/api/refresh":
                self.send_json(run_agent())
            elif self.path == "/api/config":
                length = int(self.headers.get("Content-Length", 0))
                update = json.loads(self.rfile.read(length) or b"{}")
                config = agent.load_config()
                config["use_claude"] = bool(update.get("use_claude"))
                agent.save_config(config)
                self.send_json(config_state())
            else:
                self.send_error(404)
        except Exception as error:
            self.send_json({"error": str(error)}, 500)

    def send_json(self, payload, status=200):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    if sys.stdout:  # ב-pythonw (משימה מתוזמנת) אין קונסול
        sys.stdout.reconfigure(encoding="utf-8")
    if not (agent.ROOT / "news-data.js").exists():
        run_agent()
    threading.Thread(target=scheduler, daemon=True).start()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), partial(Handler, directory=str(agent.ROOT)))
    agent.log(f"האתר זמין בכתובת http://localhost:{PORT}")
    if "--no-browser" not in sys.argv:
        webbrowser.open(f"http://localhost:{PORT}")
    server.serve_forever()
