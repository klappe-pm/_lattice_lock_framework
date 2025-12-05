import json
import os
import time
from typing import Dict, List, Any, Optional
import pytest

class GauntletPlugin:
    """
    Pytest plugin for Gauntlet reporting.
    
    Collects test results and generates JSON and GitHub Summary reports.
    
    Attributes:
        json_report (bool): Whether to generate a JSON report.
        github_report (bool): Whether to generate a GitHub Summary.
        results (List[Dict]): List of test results.
        start_time (float): Session start time.
    """
    def __init__(self, json_report: bool = False, github_report: bool = False):
        # Allow configuration via init args OR environment variables
        self.json_report = json_report or os.environ.get("GAUNTLET_JSON_REPORT") == "true"
        self.github_report = github_report or os.environ.get("GAUNTLET_GITHUB_REPORT") == "true"
        self.results: List[Dict[str, Any]] = []
        self.start_time = 0.0

    def pytest_sessionstart(self, session):
        """Hook called at the start of the session."""
        self.start_time = time.time()

    def pytest_runtest_logreport(self, report):
        """Hook called for each test report."""
        if report.when == "call":
            # Collect result for JSON report
            result = {
                "nodeid": report.nodeid,
                "outcome": report.outcome,
                "duration": report.duration,
                "error": None
            }
            
            if report.longrepr:
                result["error"] = str(report.longrepr)

            self.results.append(result)

            # GitHub Annotations
            if self.github_report and report.failed:
                # Format: ::error file={name},line={line},endLine={endLine},title={title}::{message}
                # We try to extract file and line from location if available
                fpath, lineno, domain = report.location
                # lineno is 0-indexed in pytest, GitHub wants 1-indexed? Usually.
                # Let's assume 1-indexed for safety or check docs. GitHub actions usually take 1-indexed.
                # pytest report.location lineno is 0-indexed.
                
                message = str(report.longrepr).replace("\n", "%0A")
                print(f"::error file={fpath},line={lineno+1}::Test failed: {domain}%0A{message}")

    def pytest_sessionfinish(self, session, exitstatus):
        """Hook called at the end of the session to generate reports."""
        duration = time.time() - self.start_time
        
        if self.json_report:
            report_data = {
                "created": time.time(),
                "duration": duration,
                "exitcode": exitstatus,
                "tests": self.results,
                "summary": {
                    "total": len(self.results),
                    "passed": len([r for r in self.results if r["outcome"] == "passed"]),
                    "failed": len([r for r in self.results if r["outcome"] == "failed"]),
                    "skipped": len([r for r in self.results if r["outcome"] == "skipped"]),
                }
            }
            with open("gauntlet_report.json", "w") as f:
                json.dump(report_data, f, indent=2)
                
        if self.github_report:
            # Write summary to GITHUB_STEP_SUMMARY
            summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
            if summary_file:
                passed = len([r for r in self.results if r["outcome"] == "passed"])
                failed = len([r for r in self.results if r["outcome"] == "failed"])
                skipped = len([r for r in self.results if r["outcome"] == "skipped"])
                total = len(self.results)
                
                markdown = f"""
# Gauntlet Test Summary

| Metric | Count |
| :--- | :---: |
| **Total** | {total} |
| ✅ Passed | {passed} |
| ❌ Failed | {failed} |
| ⚠️ Skipped | {skipped} |
| ⏱️ Duration | {duration:.2f}s |

"""
                if failed > 0:
                    markdown += "\n## Failures\n\n"
                    for r in self.results:
                        if r["outcome"] == "failed":
                            markdown += f"- **{r['nodeid']}**\n"
                            if r["error"]:
                                markdown += f"  ```\n  {r['error']}\n  ```\n"

                with open(summary_file, "a") as f:
                    f.write(markdown)
