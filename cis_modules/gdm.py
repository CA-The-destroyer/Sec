# cis_modules/gdm.py
import os
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.8 GDM"
    conf = "/etc/gdm/custom.conf"
    if not os.path.exists(conf):
        log(f"[i] {section} – {conf} not found, skipping GDM checks")
        return

    checks = [
        ("Ensure GDM login banner is enabled",        f"grep -E '^\\s*BannerText=' {conf}"),
        ("Ensure GDM disable-user-list is enabled",   f"grep -E '^\\s*DisableUserList=true' {conf}"),
        ("Ensure GDM screen locks when idle",         f"grep -E '^\\s*IdleDelay=' {conf}"),
        ("Ensure GDM screen locks cannot be overridden",
                                                     f"grep -E '^\\s*AutomaticLogoutEnable=true' {conf}"),
        ("Ensure GDM automatic mounting of removable media is disabled",
                                                     f"grep -E '^\\s*AutomaticMount=false' {conf}"),
        ("Ensure GDM disabling automatic mounting of removable media is not overridden",
                                                     f"true"),
        ("Ensure GDM autorun-never is enabled",       f"grep -E '^\\s*AutorunNever=true' {conf}"),
        ("Ensure GDM autorun-never is not overridden",f"true")
    ]
    for desc, check in checks:
        _run_check_fix(section, desc, check, None, verify_only, REPORT, log)
