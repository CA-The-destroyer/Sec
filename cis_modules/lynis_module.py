# cis_modules/lynis_module.py

import logging
import subprocess
import shutil
import sys
import re
from pathlib import Path

def _has_cmd(cmd):
    return shutil.which(cmd) is not None

def _get_major_version():
    """Read /etc/os-release for VERSION_ID and return the integer portion."""
    try:
        for line in Path('/etc/os-release').read_text().splitlines():
            if line.startswith('VERSION_ID'):
                # e.g. VERSION_ID="8" or VERSION_ID="8.6"
                m = re.search(r'"?(\d+)', line)
                if m:
                    return m.group(1)
    except Exception:
        pass
    return None

def install():
    """Install Lynis using apt or dnf/yum (with EPEL fallback)."""
    logging.info("📦 Installing Lynis…")

    if _has_cmd('apt'):
        # Debian / Ubuntu
        subprocess.run(['apt', 'update', '-y'], check=True)
        subprocess.run(['apt', 'install', '-y', 'lynis'], check=True)

    elif _has_cmd('dnf') or _has_cmd('yum'):
        # RHEL / CentOS / AlmaLinux
        pm = 'dnf' if _has_cmd('dnf') else 'yum'

        # 1) Try the normal epel-release package
        try:
            logging.info(f"→ Installing epel-release via {pm}")
            subprocess.run([pm, 'install', '-y', 'epel-release'], check=True)
        except subprocess.CalledProcessError:
            # fallback to direct RPM
            ver = _get_major_version()
            if not ver:
                logging.error("❌ Could not detect OS version for EPEL fallback.")
                sys.exit(1)
            url = f'https://dl.fedoraproject.org/pub/epel/epel-release-latest-{ver}.noarch.rpm'
            logging.warning(f"⚠️  epel-release install failed; falling back to {url}")
            subprocess.run([pm, 'install', '-y', url], check=True)

        # 2) Finally install Lynis itself
        subprocess.run([pm, 'install', '-y', 'lynis'], check=True)

    else:
        logging.error("❌ No supported package manager found (apt or dnf/yum).")
        sys.exit(1)

    logging.info("✅ Lynis installed.")

def audit(auditor_name='cis_hardening_script'):
    """Run a quick Lynis audit; if the lynis binary is missing, install and retry."""
    cmd = ['lynis', 'audit', 'system', '--quick', f'--auditor={auditor_name}']
    logging.info("🔍 Running Lynis audit…")
    try:
        subprocess.run(cmd, check=False)
    except FileNotFoundError:
        logging.warning("⚠️  Lynis binary not found; installing now…")
        install()
        subprocess.run(cmd, check=False)
    logging.info("🧪 Lynis audit completed.")
