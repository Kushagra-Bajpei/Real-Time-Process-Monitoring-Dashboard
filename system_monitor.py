import http.server
import socketserver
import webbrowser
import threading
import time
from datetime import datetime

import psutil

print("🚀 Starting System Monitor (Web)")
print("📊 This will open in your browser.")
print("🛑 Press Ctrl+C in the terminal to stop.\n")


class ProcessMonitor:
    def __init__(self):
        self.data = self.read_system_data()

    def read_system_data(self):
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.5)
        per_core = psutil.cpu_percent(interval=None, percpu=True)

        # Memory
        mem = psutil.virtual_memory()
        mem_total_gb = mem.total / (1024 ** 3)
        mem_used_gb = mem.used / (1024 ** 3)
        mem_percent = mem.percent

        # Disk (root drive)
        disk = psutil.disk_usage("/")
        disk_total_gb = disk.total / (1024 ** 3)
        disk_used_gb = disk.used / (1024 ** 3)
        disk_percent = disk.percent

        # Processes
        processes = []
        # warm up cpu_percent
        for p in psutil.process_iter():
            try:
                p.cpu_percent(interval=None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        time.sleep(0.2)

        for proc in psutil.process_iter(
            ["pid", "name", "cpu_percent", "memory_percent", "status"]
        ):
            try:
                info = proc.info
                info["status"] = str(info["status"])
                processes.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
        top_processes = processes[:10]

        return {
            "cpu": cpu_percent,
            "per_core": per_core,
            "mem_percent": mem_percent,
            "mem_used": mem_used_gb,
            "mem_total": mem_total_gb,
            "disk_used": disk_used_gb,
            "disk_total": disk_total_gb,
            "disk_percent": disk_percent,
            "processes": top_processes,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "total_processes": len(processes),
            "core_count": len(per_core),
        }

    def update_data(self):
        while True:
            self.data = self.read_system_data()
            time.sleep(2)


monitor = ProcessMonitor()
threading.Thread(target=monitor.update_data, daemon=True).start()

# Completely new UI (light dashboard style)
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>System Monitor</title>
    <meta http-equiv="refresh" content="3">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background-color: #f3f4f6;
            color: #111827;
        }
        .app-shell {
            display: flex;
            min-height: 100vh;
        }
        .sidebar {
            width: 230px;
            background: #111827;
            color: #e5e7eb;
            padding: 20px 18px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .logo {
            font-weight: 700;
            font-size: 1.2rem;
            letter-spacing: 0.04em;
            padding-bottom: 14px;
            border-bottom: 1px solid #374151;
            margin-bottom: 10px;
        }
        .logo span {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 999px;
            background: #2563eb;
            color: white;
            font-size: 0.75rem;
            margin-left: 4px;
        }
        .side-section-title {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #9ca3af;
            margin-top: 4px;
        }
        .side-item {
            font-size: 0.9rem;
            padding: 8px 10px;
            border-radius: 8px;
            cursor: default;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .side-item.active {
            background: #1d4ed8;
            color: white;
        }
        .side-badge {
            font-size: 0.7rem;
            padding: 2px 7px;
            border-radius: 999px;
            background: rgba(249,250,251,0.12);
        }
        .side-footer {
            margin-top: auto;
            font-size: 0.7rem;
            color: #9ca3af;
        }

        .main {
            flex: 1;
            padding: 18px 22px 26px;
        }
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
        }
        .top-title {
            font-size: 1.4rem;
            font-weight: 600;
        }
        .subtitle {
            color: #6b7280;
            font-size: 0.9rem;
        }
        .badge-time {
            font-size: 0.8rem;
            padding: 6px 10px;
            border-radius: 999px;
            background: #e5e7eb;
            color: #374151;
        }

        .grid-3 {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
            gap: 16px;
            margin-bottom: 18px;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 14px 16px 16px;
            box-shadow: 0 1px 3px rgba(15,23,42,0.08);
            border: 1px solid #e5e7eb;
        }
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 10px;
        }
        .card-title {
            font-size: 0.9rem;
            font-weight: 600;
            color: #4b5563;
        }
        .card-tag {
            font-size: 0.7rem;
            padding: 3px 8px;
            border-radius: 999px;
            background: #eff6ff;
            color: #1d4ed8;
        }
        .stat-main {
            display: flex;
            align-items: baseline;
            gap: 4px;
        }
        .stat-value {
            font-size: 1.9rem;
            font-weight: 700;
        }
        .stat-unit {
            font-size: 0.8rem;
            color: #6b7280;
        }
        .progress-bar {
            margin-top: 10px;
            height: 9px;
            border-radius: 999px;
            position: relative;
            background: #e5e7eb;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            border-radius: 999px;
            transition: width 0.3s ease-out;
        }
        .progress-cpu { background: linear-gradient(to right, #22c55e, #15803d); }
        .progress-mem { background: linear-gradient(to right, #60a5fa, #1d4ed8); }
        .progress-disk { background: linear-gradient(to right, #fb923c, #c2410c); }

        .stat-footer {
            margin-top: 6px;
            font-size: 0.78rem;
            color: #6b7280;
            display: flex;
            justify-content: space-between;
        }

        .lower-grid {
            display: grid;
            grid-template-columns: minmax(0, 2fr) minmax(0, 1.4fr);
            gap: 16px;
            margin-top: 4px;
        }
        @media (max-width: 900px) {
            .app-shell { flex-direction: column; }
            .sidebar { width: 100%; flex-direction: row; align-items: center; gap: 10px; }
            .side-footer { display: none; }
            .lower-grid { grid-template-columns: minmax(0, 1fr); }
        }

        .table-card { overflow: hidden; }
        table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
        thead { background: #f9fafb; }
        th, td {
            padding: 9px 10px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        th {
            font-weight: 600;
            color: #4b5563;
            font-size: 0.78rem;
        }
        tbody tr:hover { background: #f3f4f6; }

        .process-name { font-weight: 500; }
        .status-chip {
            padding: 3px 9px;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        .status-running { background: #dcfce7; color: #166534; }
        .status-sleeping { background: #fef3c7; color: #92400e; }
        .status-other { background: #e5e7eb; color: #374151; }

        .mini-meter {
            height: 6px;
            border-radius: 999px;
            background: #e5e7eb;
            overflow: hidden;
        }
        .mini-fill-cpu { background: #22c55e; height: 100%; }
        .mini-fill-mem { background: #3b82f6; height: 100%; }

        .core-list-title {
            font-size: 0.85rem;
            font-weight: 600;
            color: #4b5563;
            margin-bottom: 6px;
        }
        .core-list {
            list-style: none;
            max-height: 220px;
            overflow-y: auto;
        }
        .core-list li {
            display: flex;
            justify-content: space-between;
            padding: 5px 0;
            border-bottom: 1px dashed #e5e7eb;
            font-size: 0.8rem;
        }
        .core-label { color: #4b5563; }
        .core-value { font-weight: 600; color: #1d4ed8; }

        .pill {
            font-size: 0.75rem;
            padding: 4px 9px;
            border-radius: 999px;
            background: #e5e7eb;
            color: #374151;
        }
    </style>
</head>
<body>
<div class="app-shell">
    <aside class="sidebar">
        <div class="logo">
            sys-monitor
            <span>LIVE</span>
        </div>
        <div class="side-section-title">Overview</div>
        <div class="side-item active">
            <span>Dashboard</span>
            <span class="side-badge">{{TOTAL_PROCESSES}} proc</span>
        </div>
        <div class="side-item">
            <span>CPU cores</span>
            <span class="side-badge">{{CORE_COUNT}}</span>
        </div>
        <div class="side-footer">
            Updated at {{TIMESTAMP}}<br>
            Localhost web monitor
        </div>
    </aside>

    <main class="main">
        <header class="top-bar">
            <div>
                <div class="top-title">System dashboard</div>
                <div class="subtitle">Simple web view of your CPU, memory, disk and active processes.</div>
            </div>
            <div class="badge-time">Last refresh: {{TIMESTAMP}}</div>
        </header>

        <section class="grid-3">
            <div class="card">
                <div class="card-header">
                    <div class="card-title">CPU usage</div>
                    <div class="card-tag">live</div>
                </div>
                <div class="stat-main">
                    <span class="stat-value">{{CPU_PERCENT}}</span>
                    <span class="stat-unit">%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill progress-cpu" style="width: {{CPU_PERCENT}}%;"></div>
                </div>
                <div class="stat-footer">
                    <span>{{CORE_COUNT}} logical cores</span>
                    <span>Load: {{CPU_PERCENT}}%</span>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">Memory</div>
                    <div class="card-tag">RAM</div>
                </div>
                <div class="stat-main">
                    <span class="stat-value">{{MEMORY_PERCENT}}</span>
                    <span class="stat-unit">%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill progress-mem" style="width: {{MEMORY_PERCENT}}%;"></div>
                </div>
                <div class="stat-footer">
                    <span>{{MEMORY_USED}} GB used</span>
                    <span>{{MEMORY_TOTAL}} GB total</span>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">Disk</div>
                    <div class="card-tag">system</div>
                </div>
                <div class="stat-main">
                    <span class="stat-value">{{DISK_PERCENT}}</span>
                    <span class="stat-unit">%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill progress-disk" style="width: {{DISK_PERCENT}}%;"></div>
                </div>
                <div class="stat-footer">
                    <span>{{DISK_USED}} GB used</span>
                    <span>{{DISK_TOTAL}} GB total</span>
                </div>
            </div>
        </section>

        <section class="lower-grid">
            <div class="card table-card">
                <div class="card-header">
                    <div class="card-title">Top processes (by CPU)</div>
                    <div class="pill">{{TOTAL_PROCESSES}} processes total</div>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>PID</th>
                            <th>Process</th>
                            <th>CPU</th>
                            <th>Memory</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {{PROCESS_ROWS}}
                    </tbody>
                </table>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="card-title">Per-core CPU load</div>
                    <div class="pill">logical cores</div>
                </div>
                <div class="core-list-title">Current usage</div>
                <ul class="core-list">
                    {{CORE_LIST}}
                </ul>
            </div>
        </section>
    </main>
</div>
</body>
</html>
"""


class MonitorHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            d = monitor.data

            html = HTML_CONTENT
            html = html.replace("{{CPU_PERCENT}}", f"{d['cpu']:.1f}")
            html = html.replace("{{MEMORY_PERCENT}}", f"{d['mem_percent']:.1f}")
            html = html.replace("{{DISK_PERCENT}}", f"{d['disk_percent']:.1f}")
            html = html.replace("{{MEMORY_USED}}", f"{d['mem_used']:.1f}")
            html = html.replace("{{MEMORY_TOTAL}}", f"{d['mem_total']:.1f}")
            html = html.replace("{{DISK_USED}}", f"{d['disk_used']:.1f}")
            html = html.replace("{{DISK_TOTAL}}", f"{d['disk_total']:.1f}")
            html = html.replace("{{TOTAL_PROCESSES}}", str(d["total_processes"]))
            html = html.replace("{{CORE_COUNT}}", str(d["core_count"]))
            html = html.replace("{{TIMESTAMP}}", d["timestamp"])

            # per-core list HTML
            core_items = ""
            for idx, val in enumerate(d["per_core"]):
                core_items += (
                    f"<li><span class='core-label'>Core {idx}</span>"
                    f"<span class='core-value'>{val:.0f}%</span></li>"
                )
            html = html.replace("{{CORE_LIST}}", core_items)

            # process rows
            rows = ""
            for p in d["processes"]:
                status_raw = p.get("status", "").lower()
                if "run" in status_raw:
                    status_class = "status-running"
                elif "sleep" in status_raw:
                    status_class = "status-sleeping"
                else:
                    status_class = "status-other"

                cpu = max(0.0, min(p["cpu_percent"], 100.0))
                mem = max(0.0, min(p["memory_percent"], 100.0))

                rows += f"""
<tr>
    <td>{p['pid']}</td>
    <td class="process-name">{p.get('name','')}</td>
    <td>
        <div style="display:flex;align-items:center;gap:6px;">
            <span>{cpu:.1f}%</span>
            <div class="mini-meter"><div class="mini-fill-cpu" style="width:{cpu:.1f}%"></div></div>
        </div>
    </td>
    <td>
        <div style="display:flex;align-items:center;gap:6px;">
            <span>{mem:.1f}%</span>
            <div class="mini-meter"><div class="mini-fill-mem" style="width:{mem:.1f}%"></div></div>
        </div>
    </td>
    <td><span class="status-chip {status_class}">{status_raw or "n/a"}</span></td>
</tr>
"""
            html = html.replace("{{PROCESS_ROWS}}", rows)

            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
        else:
            super().do_GET()


def start_server():
    for port in (8000, 8001, 8002, 8080):
        try:
            with socketserver.TCPServer(("", port), MonitorHandler) as httpd:
                print(f"✅ Open: http://localhost:{port}")
                print("🔄 Page refreshes every 3 seconds.")
                try:
                    webbrowser.open(f"http://localhost:{port}")
                except Exception:
                    pass
                httpd.serve_forever()
            break
        except OSError:
            continue
    else:
        print("❌ Could not bind to any port.")


if __name__ == "__main__":
    start_server()
