# cis_modules/gdm.py

from cis_modules import _run_check_fix


def run_section(verify_only, REPORT, log):
    section = "1.8 Configure GNOME Display Manager"

    # 1.8.2 Ensure GDM login banner is configured
    _run_check_fix(
        section,
        "Ensure GDM login banner is configured",
        "grep -Eq '^\s*Banner=.*gdm_banner\.html' /etc/gdm/custom.conf",
        (
            "mkdir -p /etc/gdm && "
            "cp /etc/gdm/custom.conf /etc/gdm/custom.conf.bak 2>/dev/null || true && "
            "grep -Eq '^\s*\[security\]' /etc/gdm/custom.conf || echo '[security]' >> /etc/gdm/custom.conf && "
            "grep -Eq '^\s*Banner=' /etc/gdm/custom.conf && sed -i 's|^\s*Banner=.*|Banner=/etc/gdm/gdm_banner.html|' /etc/gdm/custom.conf || echo 'Banner=/etc/gdm/gdm_banner.html' >> /etc/gdm/custom.conf"
        ),
        verify_only, REPORT, log
    )

    # 1.8.3 Ensure GDM disable-user-list option is enabled
    _run_check_fix(
        section,
        "Ensure GDM disable-user-list option is enabled",
        "grep -Eq '^\s*DisableUserList=true' /etc/gdm/custom.conf",
        (
            "grep -Eq '^\s*\[security\]' /etc/gdm/custom.conf || echo '[security]' >> /etc/gdm/custom.conf && "
            "grep -Eq '^\s*DisableUserList=' /etc/gdm/custom.conf && sed -i 's|^\s*DisableUserList=.*|DisableUserList=true|' /etc/gdm/custom.conf || echo 'DisableUserList=true' >> /etc/gdm/custom.conf"
        ),
        verify_only, REPORT, log
    )

    # 1.8.4 Ensure GDM screen locks when the user is idle
    _run_check_fix(
        section,
        "Ensure GDM screen locks when the user is idle",
        "grep -Eq '^\s*AutomaticLoginEnable=false' /etc/gdm/custom.conf",
        (
            "grep -Eq '^\s*\[daemon\]' /etc/gdm/custom.conf || echo '[daemon]' >> /etc/gdm/custom.conf && "
            "grep -Eq '^\s*AutomaticLoginEnable=' /etc/gdm/custom.conf && sed -i 's|^\s*AutomaticLoginEnable=.*|AutomaticLoginEnable=false|' /etc/gdm/custom.conf || echo 'AutomaticLoginEnable=false' >> /etc/gdm/custom.conf"
        ),
        verify_only, REPORT, log
    )

    # 1.8.5 Ensure GDM screen locks cannot be overridden
    _run_check_fix(
        section,
        "Ensure GDM screen locks cannot be overridden",
        "grep -Eq '^\s*DisableLockScreen=false' /etc/gdm/custom.conf",
        (
            "grep -Eq '^\s*\[security\]' /etc/gdm/custom.conf || echo '[security]' >> /etc/gdm/custom.conf && "
            "grep -Eq '^\s*DisableLockScreen=' /etc/gdm/custom.conf && sed -i 's|^\s*DisableLockScreen=.*|DisableLockScreen=false|' /etc/gdm/custom.conf || echo 'DisableLockScreen=false' >> /etc/gdm/custom.conf"
        ),
        verify_only, REPORT, log
    )

    # 1.8.6 Ensure GDM automatic mounting of removable media is disabled
    _run_check_fix(
        section,
        "Ensure GDM automatic mounting of removable media is disabled",
        "grep -Eq '^\s*AutomaticMount=false' /etc/gdm/custom.conf",
        (
            "grep -Eq '^\s*\[greeter\]' /etc/gdm/custom.conf || echo '[greeter]' >> /etc/gdm/custom.conf && "
            "grep -Eq '^\s*AutomaticMount=' /etc/gdm/custom.conf && sed -i 's|^\s*AutomaticMount=.*|AutomaticMount=false|' /etc/gdm/custom.conf || echo 'AutomaticMount=false' >> /etc/gdm/custom.conf"
        ),
        verify_only, REPORT, log
    )

    # 1.8.7 Ensure GDM disabling automatic mounting of removable media is not overridden
    _run_check_fix(
        section,
        "Ensure GDM disabling automatic mounting of removable media is not overridden",
        "grep -Eq '^\s*AutomaticMountOverride=false' /etc/gdm/custom.conf",
        (
            "grep -Eq '^\s*\[greeter\]' /etc/gdm/custom.conf || echo '[greeter]' >> /etc/gdm/custom.conf && "
            "grep -Eq '^\s*AutomaticMountOverride=' /etc/gdm/custom.conf && sed -i 's|^\s*AutomaticMountOverride=.*|AutomaticMountOverride=false|' /etc/gdm/custom.conf || echo 'AutomaticMountOverride=false' >> /etc/gdm/custom.conf"
        ),
        verify_only, REPORT, log
    )

    # 1.8.8 Ensure GDM autorun-never is enabled
    _run_check_fix(
        section,
        "Ensure GDM autorun-never is enabled",
        "grep -Eq '^\s*Autorun-never=true' /etc/gdm/custom.conf",
        (
            "grep -Eq '^\s*\[daemon\]' /etc/gdm/custom.conf || echo '[daemon]' >> /etc/gdm/custom.conf && "
            "grep -Eq '^\s*Autorun-never=' /etc/gdm/custom.conf && sed -i 's|^\s*Autorun-never=.*|Autorun-never=true|' /etc/gdm/custom.conf || echo 'Autorun-never=true' >> /etc/gdm/custom.conf"
        ),
        verify_only, REPORT, log
    )

    # 1.8.9 Ensure GDM autorun-never is not overridden
    _run_check_fix(
        section,
        "Ensure GDM autorun-never is not overridden",
        "grep -Eq '^\s*Autorun-never-override=false' /etc/gdm/custom.conf",
        (
            "grep -Eq '^\s*\[daemon\]' /etc/gdm/custom.conf || echo '[daemon]' >> /etc/gdm/custom.conf && "
            "grep -Eq '^\s*Autorun-never-override=' /etc/gdm/custom.conf && sed -i 's|^\s*Autorun-never-override=.*|Autorun-never-override=false|' /etc/gdm/custom.conf || echo 'Autorun-never-override=false' >> /etc/gdm/custom.conf"
        ),
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
