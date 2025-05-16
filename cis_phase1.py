#!/usr/bin/env python3
"""
cis_phase1.py
CIS Level 1 Compliance Orchestrator with interactive module selection and HTML Reporting
"""

import argparse
import os
import sys
from datetime import datetime

# Make sure cis_modules/ is on our Python path
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

REPORT = []
LOG_FILE = f"cis_phase1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def log(message: str):
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")
    print(message)

def generate_report():
    report_name = f"cis_phase1_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(report_name, "w") as f:
        f.write("<html><head><title>CIS Level 1 Report</title></head><body>")
        f.write("<h1>CIS Level 1 Compliance Report</h1><table border='1'>")
        f.write("<tr><th>Section</th><th>Description</th><th>Status</th></tr>")
        for section, desc, status in REPORT:
            color = "#ccffcc" if status in ("Compliant", "Fixed", "Success") else "#ffcccc"
            f.write(f"<tr style='background-color:{color}'>"
                    f"<td>{section}</td><td>{desc}</td><td>{status}</td></tr>")
        f.write("</table></body></html>")
    log(f"[✔] HTML report saved to {report_name}")

def parse_selection(modules):
    """Interactive menu to pick modules, or run all if blank/'all'."""
    print("\nAvailable modules:")
    for idx, mod in enumerate(modules, 1):
        print(f" {idx}. {mod.split('.')[-1]}")
    sel = input("Modules to run (e.g. 1,3-5 or 'all'): ").strip().lower()
    if not sel or sel in ("all", "*"):
        return modules
    chosen = set()
    for part in sel.split(','):
        if '-' in part:
            start, end = part.split('-', 1)
            chosen.update(range(int(start)-1, int(end)))
        else:
            chosen.add(int(part)-1)
    return [modules[i] for i in sorted(chosen) if 0 <= i < len(modules)]

def main():
    parser = argparse.ArgumentParser(description="CIS Level 1 Compliance Orchestrator")
    parser.add_argument("--verify-only", action="store_true", help="Audit only (no fixes)")
    args = parser.parse_args()

    if os.geteuid() != 0:
        log("ERROR: Must be run as root.")
        sys.exit(1)

    mode = "Verification" if args.verify_only else "Enforcement"
    log(f"[*] CIS Level 1 – {mode} started at {datetime.now()}")

    # List of modules – ensure each of these maps to a file in cis_modules/
    modules = [
        "cis_modules.filesystem",
        "cis_modules.packages",
        "cis_modules.selinux",
        "cis_modules.bootloader",
        "cis_modules.auth_and_lockdown",
        "cis_modules.crypto_policy",
        "cis_modules.banners",
        "cis_modules.gdm",
        "cis_modules.chrony",
        "cis_modules.network",        # includes telnet & bluetooth & sysctls
        "cis_modules.firewall",
        "cis_modules.nftables",
        "cis_modules.sudo",
        "cis_modules.pam_packages",   # installs pam modules
        "cis_modules.pam_config",     # complexity & history & nullok
        "cis_modules.shadow",         # expiration, warning, inactive
        "cis_modules.aide",
        "cis_modules.journald",
        "cis_modules.rsyslog",
        "cis_modules.logfiles",
        "cis_modules.maintenance",    # world-owned files
    ]

    # Let user select subset if desired
    selected = parse_selection(modules)

    # Run each
    for mod_path in selected:
        log(f"[*] Running: {mod_path}")
        try:
            mod = __import__(mod_path, fromlist=["run_section"])
            mod.run_section(args.verify_only, REPORT, log)
        except ImportError:
            log(f"[!] Module not found: {mod_path}")
        except Exception as e:
            log(f"[✗] Error in {mod_path}: {e}")

    # Final report
    generate_report()
    log(f"[*] CIS Level 1 – {mode} completed at {datetime.now()}")

if __name__ == "__main__":
    main()
