
# IMPLEMENTATION PROTOTYPE (Agent D_7_5)
# Task 7.5: Security Hardening (Secret Scanner)

import re
from pathlib import Path

SENSITIVE_PATTERNS = [
    r"AKIA[0-9A-Z]{16}", # AWS Access Key
    r"sk-proj-[a-zA-Z0-9]{20,}", # OpenAI Key
]

def scan_for_secrets(target_dir: str = "."):
    print(f"[SECURITY] Scanning {target_dir} for secrets...")
    root = Path(target_dir)
    findings = []

    for fpath in root.glob("**/*.py"):
        if "scripts/" in str(fpath): continue # Skip our own scripts

        content = fpath.read_text(errors='ignore')
        for pattern in SENSITIVE_PATTERNS:
            if re.search(pattern, content):
                findings.append(f"{fpath}: Matches {pattern}")

    if findings:
        print(f"[FAIL] Found {len(findings)} potential secrets!")
        for f in findings:
            print(f"  - {f}")
    else:
        print("[PASS] No patterns matched.")

if __name__ == "__main__":
    # Create a dummy file to test detection
    with open("dummy_secret.py", "w") as f:
        f.write("key = 'AKIA1234567890ABCDEF'")

    scan_for_secrets()

    # Cleanup
    Path("dummy_secret.py").unlink()
