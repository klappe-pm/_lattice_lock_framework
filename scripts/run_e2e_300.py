import sys
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime

REPORT_XML = "e2e_report.xml"
SUMMARY_MD = "e2e_summary.md"

def run_tests():
    print(f"Running E2E tests... Output to {REPORT_XML}")
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/e2e_300/test_e2e_matrix.py",
        f"--junitxml={REPORT_XML}",
        "-v"
    ]
    subprocess.run(cmd)

def generate_report():
    print("Parsing test results...")
    try:
        tree = ET.parse(REPORT_XML)
        root = tree.getroot()
    except FileNotFoundError:
        print("Error: Test report XML not found.")
        return

    passed_no_issues = []
    passed_improvements = [] # Placeholder
    failed_fix = []
    failed_obsolete = []

    # Flatten testsuites -> testsuite -> testcase
    testcases = root.findall(".//testcase")
    
    for tc in testcases:
        name = tc.get("name")
        classname = tc.get("classname")
        full_name = f"{classname}::{name}"
        
        failure = tc.find("failure")
        error = tc.find("error")
        skipped = tc.find("skipped")
        
        if failure is not None or error is not None:
            message = (failure.get("message") if failure is not None else error.get("message")) or "Unknown Error"
            
            # Heuristic for "obsolete"
            if "ImportError" in message or "ModuleNotFoundError" in message:
                failed_obsolete.append(f"- [ ] **{full_name}**: {message}")
            else:
                failed_fix.append(f"- [ ] **{full_name}**: {message}")
        elif skipped is not None:
            passed_improvements.append(f"- [ ] **{full_name}**: Skipped ({skipped.get('message')})")
        else:
            # Check for warnings in system-out if available? (simulated here)
            # For now assume clean pass
            passed_no_issues.append(f"- [x] **{full_name}**")

    # Generate Markdown
    md_content = f"""# E2E Test Summary Report
**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Tests**: {len(testcases)}

## Summary Qualifiers
- **Passed**: {len(passed_no_issues)}
- **Passed (Checks)**: {len(passed_improvements)}
- **Failed (Fix Required)**: {len(failed_fix)}
- **Failed (Obsolete)**: {len(failed_obsolete)}

## Failed (Fix Required)
{chr(10).join(failed_fix) if failed_fix else "None"}

## Failed (Obsolete/Delete)
{chr(10).join(failed_obsolete) if failed_obsolete else "None"}

## Passed (Improvements Needed)
{chr(10).join(passed_improvements) if passed_improvements else "None"}

## Passed (Clean)
<details>
<summary>View {len(passed_no_issues)} Passed Tests</summary>

{chr(10).join(passed_no_issues)}
</details>
"""

    with open(SUMMARY_MD, "w") as f:
        f.write(md_content)
    
    print(f"Summary report generated: {SUMMARY_MD}")

if __name__ == "__main__":
    run_tests()
    generate_report()
