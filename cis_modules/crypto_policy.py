# cis_modules/crypto_policy.py

import os
from glob import glob
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.6 Crypto Policy"

    # Directories to clean
    dirs = [
        "/etc/crypto-policies/back-ends",
        "/etc/crypto-policies/local.d"
    ]

    # 1.6.3 Ensure SHA1 is disabled everywhere
    # Build a combined grep command for presence
    grep_paths = " ".join(dirs)
    check_cmd = f"! grep -Riq 'sha1' {grep_paths}"
    fix_cmd_lines = []
    for d in dirs:
        # Only try to clean dirs that exist
        fix_cmd_lines.append(
            f"if [ -d '{d}' ]; then "
            f"  grep -Rl 'sha1' '{d}' | xargs -r sed -i '/sha1/Id'; "
            "fi"
        )
    # Finally reload
    fix_cmd_lines.append("update-crypto-policies --reload")
    fix_cmd = " && ".join(fix_cmd_lines)

    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables SHA1 everywhere",
        check_cmd,
        fix_cmd,
        verify_only, REPORT, log
    )

    #
    # The rest of the SSH crypto-policy controls remain unchanged...
    #

    # 1.6.5 Disable aes128-cbc
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables AES-CBC for SSH",
        "grep -q 'Ciphers.*-aes128-cbc' /etc/crypto-policies/back-ends/openssh.config",
        "echo 'Ciphers -aes128-cbc' >> /etc/crypto-policies/back-ends/openssh.config && update-crypto-policies --reload",
        verify_only, REPORT, log
    )

    # 1.6.6 Disable chacha20-poly1305
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables chacha20-poly1305 for SSH",
        "grep -q 'Ciphers.*-chacha20-poly1305@openssh.com' /etc/crypto-policies/back-ends/openssh.config",
        "echo 'Ciphers -chacha20-poly1305@openssh.com' >> /etc/crypto-policies/back-ends/openssh.config && update-crypto-policies --reload",
        verify_only, REPORT, log
    )

    # 1.6.7 Disable EtM
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables EtM for SSH",
        "grep -q 'MACs.*-hmac-etm' /etc/crypto-policies/back-ends/openssh.config",
        "echo 'MACs -hmac-etm' >> /etc/crypto-policies/back-ends/openssh.config && update-crypto-policies --reload",
        verify_only, REPORT, log
    )
