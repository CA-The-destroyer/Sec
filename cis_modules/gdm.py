# cis_modules/gdm.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.8 GDM"

    # GDM login banner
    _run_check_fix(
        section,
        "Ensure GDM login banner is configured",
        "grep -q 'banner-message-enable=true' /etc/dconf/db/gdm.d/01-banner-message",
        "echo -e '[org/gnome/login-screen]\\n banner-message-enable=true\\n banner-message-text=\"Authorized users only.\"' > /etc/dconf/db/gdm.d/01-banner-message && dconf update",
        verify_only, REPORT, log
    )

    # GDM disable-user-list
    _run_check_fix(
        section,
        "Ensure GDM disable-user-list option is enabled",
        "grep -q 'disable-user-list=true' /etc/dconf/db/gdm.d/02-disable-users",
        "echo -e '[org/gnome/login-screen]\\n disable-user-list=true' > /etc/dconf/db/gdm.d/02-disable-users && dconf update",
        verify_only, REPORT, log
    )

    # GDM screen locks when idle
    _run_check_fix(
        section,
        "Ensure GDM screen locks when the user is idle",
        "grep -q 'idle-delay=uint32 300' /etc/dconf/db/gdm.d/03-idle-lock",
        "echo -e '[org/gnome/desktop/session]\\n idle-delay=uint32 300' > /etc/dconf/db/gdm.d/03-idle-lock && dconf update",
        verify_only, REPORT, log
    )

    # GDM locking cannot be overridden
    _run_check_fix(
        section,
        "Ensure GDM screen locks cannot be overridden",
        "grep -q 'logout-enabled=false' /etc/dconf/db/gdm.d/04-lock-policy",
        "echo -e '[org/gnome/settings-daemon/plugins/media-keys]\\n logout-enabled=false' > /etc/dconf/db/gdm.d/04-lock-policy && dconf update",
        verify_only, REPORT, log
    )

    # GDM auto-mount disabled
    _run_check_fix(
        section,
        "Ensure GDM automatic mounting of removable media is disabled",
        "grep -q 'automount=false' /etc/dconf/db/gdm.d/05-automount",
        "echo -e '[org/gnome/desktop/media-handling]\\n automount=false' > /etc/dconf/db/gdm.d/05-automount && dconf update",
        verify_only, REPORT, log
    )

    # GDM auto-mount not overridden
    _run_check_fix(
        section,
        "Ensure GDM disabling automatic mounting of removable media is not overridden",
        "grep -q 'automount-ignore=true' /etc/dconf/db/gdm.d/06-automount-ignore",
        "echo -e '[org/gnome/desktop/media-handling]\\n automount-ignore=true' > /etc/dconf/db/gdm.d/06-automount-ignore && dconf update",
        verify_only, REPORT, log
    )

    # GDM autorun-never enabled
    _run_check_fix(
        section,
        "Ensure GDM autorun-never is enabled",
        "grep -q 'autorun-never=true' /etc/dconf/db/gdm.d/07-autorun",
        "echo -e '[org/gnome/desktop/media-handling]\\n autorun-never=true' > /etc/dconf/db/gdm.d/07-autorun && dconf update",
        verify_only, REPORT, log
    )

    # GDM autorun-never not overridden
    _run_check_fix(
        section,
        "Ensure GDM autorun-never is not overridden",
        "grep -q 'autorun-never=true' /etc/dconf/db/gdm.d/08-autorun-ignore",
        "echo -e '[org/gnome/desktop/media-handling]\\n autorun-never=true' > /etc/dconf/db/gdm.d/08-autorun-ignore && dconf update",
        verify_only, REPORT, log
    )
