#!/usr/bin/env python3
"""
cis_phase1.py
CIS Level 1 Compliance Orchestrator with HTML Reporting
Runs all Level 1 checks as separate modules under cis_modules/.
Usage:
  sudo python3 cis_phase1.py [--verify-only]

--verify-only   Run in audit-only mode (no remediation)
"""

import argparse
import os
import sys
import subprocess
from datetime import datetime

# Ensure cis_modules/ is on the import path
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

LOG_FILE = f"cis_phase1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
REPORT   = []

def log(msg: str):
    """Append to the log file and echo to stdout."""
    with open(LOG_FILE, "a") as f:
        f.write(msg + "\n")
    print(msg)

def generate_report():
    """Produce an HTML report of all checks and their statuses."""
    report_name = f"cis_phase1_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(report_name, "w") as f:
        f.write("<html><head><title>CIS Level 1 Compliance Report</title></head><body>")
        f.write("<h1>CIS Level 1 Compliance Report</h1>")
        f.write("<table border='1'><tr><th>Section</th><th>Description</th><th>Status</th></tr>")
        for section, desc, status in REPORT:
            color = "#ccffcc" if status in ("Compliant", "Fixed") else "#ffcccc"
            f.write(f"<tr style='background-color:{color}'><td>{section}</td><td>{desc}</td><td>{status}</td></tr>")
        f.write("</table></body></html>")
    log(f"[✔] HTML report saved to {report_name}")

def main():
    p = argparse.ArgumentParser(description="CIS Level 1 Compliance Orchestrator")
    p.add_argument("--verify-only", action="store_true", help="Audit only, no fixes")
    args = p.parse_args()

    mode = "Verification" if args.verify_only else "Enforcement"
    log(f"[*] CIS Level 1 – {mode} started: {datetime.now()}")

    modules = [
        "cis_modules.filesystem",
        "cis_modules.packages",
        "cis_modules.selinux",
        "cis_modules.bootloader",
        "cis_modules.auth_and_lockdown",
        "cis_modules.crypto_policy",
        "cis_modules.banners",
        "cis_modules.gdm",
    ]

    for mod_path in modules:
        try:
            mod = __import__(mod_path, fromlist=["run_section"])
            log(f"[*] Running section: {mod_path}")
            mod.run_section(args.verify_only, REPORT, log)
        except ImportError:
            log(f"[!] Module not found, skipping: {mod_path}")
        except Exception as e:
            log(f"[✗] Error in {mod_path}: {e}")

    generate_report()
    log(f"[✔] CIS Level 1 – {mode} complete: {datetime.now()}")

if __name__ == "__main__":
    main()
