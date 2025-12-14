
# IMPLEMENTATION PROTOTYPE (Agent C_3_4)
# Task 3.4: Status Dashboard Frontend

from pathlib import Path

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Lattice Lock Dashboard</title>
    <style>
        body { font-family: sans-serif; padding: 20px; }
        .card { border: 1px solid #ccc; padding: 15px; margin: 10px; border-radius: 5px; }
        .success { color: green; }
        .fail { color: red; }
    </style>
</head>
<body>
    <h1>Project Status</h1>
    <div id="app">Loading...</div>
    <script>
        // Mock API Call
        const status = {
            health: "98%",
            lastBuild: "SUCCESS",
            activeModels: 5,
            costToday: "$1.24"
        };
        
        document.getElementById('app').innerHTML = `
            <div class="card">
                <h3>Build Status: <span class="success">${status.lastBuild}</span></h3>
                <p>Health Score: ${status.health}</p>
                <p>Daily Cost: ${status.costToday}</p>
            </div>
        `;
    </script>
</body>
</html>
"""

def generate_dashboard():
    print("[DASHBOARD] Generating static assets...")
    Path("dashboard").mkdir(exist_ok=True)
    with open("dashboard/index.html", "w") as f:
        f.write(DASHBOARD_HTML)
    print("[DASHBOARD] Created dashboard/index.html")

if __name__ == "__main__":
    generate_dashboard()
