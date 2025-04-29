#!/usr/bin/env python3

import os
import sys
import subprocess
import shutil
from datetime import datetime

# Orchestration script for CIS Level 1 compliance on AlmaLinux
# Supports both "--verify-only" (audit) and enforcement modes
# Imports section modules from cis_modules/ directory

LOG_FILE = f"cis_phase1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
REPORT = []


def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")
    print(message)


def generate_report():
    report_file = f"cis_phase1_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(report_file, "w") as f:
        f.write("<html><head><title>CIS Level 1 Compliance Report</title></head><body>")
        f.write("<h1>CIS Level 1 Compliance Report</h1><table border='1'><tr><th>Section</th><th>Description</th><th>Status</th></tr>")
        for section, desc, status in REPORT:
            color = "#ccffcc" if status in ["Compliant", "Fixed"] else "#ffcccc"
            f.write(f"<tr style='background-color:{color}'><td>{section}</td><td>{desc}</td><td>{status}</td></tr>")
        f.write("</table></body></html>")
    log(f"[✔] Report saved to {report_file}")


def main():
    verify_only = "--verify-only" in sys.argv
    mode = "Verification" if verify_only else "Enforcement"
    log(f"[*] CIS Level 1 - {mode} start: {datetime.now()}")

    # Dynamically import and run each module in cis_modules
    modules = [
        "cis_modules.filesystem",
        "cis_modules.selinux",
        "cis_modules.bootloader",
        "cis_modules.crypto_policy",
        "cis_modules.banners",
        "cis_modules.auth_and_lockdown", 
        "cis_modules.packages",
        # add more modules as they are created
    ]
    for mod_path in modules:
        try:
            mod = __import__(mod_path, fromlist=["run_section"])
            log(f"[*] Running section: {mod_path}")
            mod.run_section(verify_only, REPORT, log)
        except ImportError as ie:
            log(f"[!] Module not found: {mod_path}, skipping.")
        except Exception as e:
            log(f"[✗] Error in {mod_path}: {e}")

    generate_report()
    log(f"[✔] CIS Level 1 - {mode} complete: {datetime.now()}")


if __name__ == "__main__":
    main()
