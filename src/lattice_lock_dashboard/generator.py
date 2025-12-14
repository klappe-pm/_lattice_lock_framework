import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DashboardGenerator:
    """
    Generates the static Admin Dashboard.
    """
    DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Lattice Lock Dashboard</title>
    <meta http-equiv="refresh" content="30">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; padding: 40px; background: #f4f6f8; }}
        .card {{ background: white; padding: 20px; margin-bottom: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .status-ok {{ color: #2e7d32; font-weight: bold; }}
        .status-err {{ color: #c62828; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>Lattice Lock Admin</h1>
    
    <div class="card">
        <h2>Project Health</h2>
        <p>Status: <span class="{status_class}">{status}</span></p>
        <p>Version: {version}</p>
    </div>
    
    <div class="card">
        <h2>Telemetry</h2>
        <p>Active Models: {active_models}</p>
    </div>
</body>
</html>
"""

    def generate(self, output_path: str = "dashboard/index.html", data: Dict[str, Any] = None):
        if data is None:
            data = {"status": "HEALTHY", "version": "2.1.0", "active_models": 5}
            
        logger.info(f"Generating dashboard to {output_path}")
        
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        html = self.DASHBOARD_TEMPLATE.format(
            status=data.get('status', 'UNKNOWN'),
            status_class="status-ok" if data.get('status') == "HEALTHY" else "status-err",
            version=data.get('version', '0.0.0'),
            active_models=data.get('active_models', 0)
        )
        
        with open(path, "w") as f:
            f.write(html)
