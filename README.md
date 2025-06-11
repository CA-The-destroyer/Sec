Firewall Ports (ICA, Registration, LDAP/FAS)

        Citrix documentation clearly states that for VDA registration and ICA traffic you must allow:

        TCP/UDP 1494, 2598 for ICA payload

        TCP 80, 443 for VDA registration with the Delivery Controller

        TCP/UDP 389, 636 if you’re using FAS or LDAP backend
        See the “Required VDA Firewall Ports” section in the Citrix Docs: **CTX227428** .


SELinux and Citrix VDA

    Citrix ships an RPM with its VDA installer that includes an SELinux policy module. Until that’s installed, SELinux must be in Permissive mode or the VDA will be blocked.
    See “Citrix Linux VDA and SELinux” in **CTX269560** .

PAM Ordering for FAS/SSSD

    The Citrix FAS integration guide shows that pam_sss.so forward_pass needs to be the first line in your system-auth stack so certificate‐based login happens before any faillock or complexity checks.
    See the “Configure PAM for FAS” section in the FAS Deployment Guide **CTX231864** .

USB Redirection

    To enable USB redirection the usb-storage module must not be blacklisted, or you must explicitly allow it in your policy.
    See **CTX215541** “USB Redirection on Linux VDA” .

  
