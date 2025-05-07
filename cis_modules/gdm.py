# cis_modules/gdm.py

import os
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.8 GDM"
    conf = "/etc/gdm/custom.conf"
    if not os.path.exists(conf):
        log(f"[i] {section} – no GDM config, skipping")
        return

    for desc, pattern in [
        ("Ensure GDM login banner is configured",       "^\\s*BannerText=.*"),
        ("Ensure GDM disable-user-list is enabled",    "^\\s*DisableUserList=true"),
        ("Ensure GDM screen locks when the user is idle","^\\s*IdleDelay=.*"),
        ("Ensure GDM screen locks cannot be overridden","^\\s*AutomaticLogoutEnable=true"),
        ("Ensure GDM auto-mount is disabled",           "^\\s*AutomaticMount=false"),
        ("Ensure GDM autorun-never is enabled",         "^\\s*AutorunNever=true"),
    ]:
        _run_check_fix(
            section,
            desc,
            f"grep -E '{pattern}' {conf}",
            None,
            verify_only, REPORT, log
        )
