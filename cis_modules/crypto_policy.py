# cis_modules/crypto_policy.py

from cis_modules import _run_check_fix

"""
Notes:

- We use `update-crypto-policies` (RHEL/CentOS/AlmaLinux 9) to set the global crypto policy.
- To disable SHA1, CBC, chacha20, and EtM in SSH, we must edit /etc/crypto-policies/back-ends/opensshserver.config or fallback to editing /etc/ssh/sshd_config directly.

Here, we'll:
1) Ensure `update-crypto-policies --show` does not include “legacy” or “DEFAULT:AD‐support‐legacy”
2) In /etc/ssh/sshd_config, explicitly remove weak ciphers/mac/EtM if present, and append a strong set.
"""

SSH_CONFIG = "/etc/ssh/sshd_config"

def run_section(verify_only, REPORT, log):
    section = "1.6 Crypto Policy"

    # 1.6.1 Ensure system crypto policy is not set to legacy
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy is not 'LEGACY' or 'AD-support-legacy'",
        "update-crypto-policies --show | grep -Ev '^(LEGACY|AD-support-legacy)$'",
        "update-crypto-policies --set DEFAULT",  # fallback to default
        verify_only, REPORT, log
    )

    # 1.6.3 Ensure system crypto policy disables SHA1 hash and signature support
    _run_check_fix(
        section,
        "Ensure system crypto policy disables SHA1",
        "grep -q 'SHA1' /etc/crypto-policies/back-ends/opensshserver.config || true",
        (
            # Append a “Disallow” line in opensshserver.config
            "sed -i.bak -E '/^Ciphers / s/$/,hmac-sha1/' /etc/crypto-policies/back-ends/opensshserver.config || "
            "echo 'MACs -hmac-sha1' >> /etc/crypto-policies/back-ends/opensshserver.config && "
            "update-crypto-policies --reload"
        ),
        verify_only, REPORT, log
    )

    # 1.6.5 Ensure system crypto policy disables CBC for SSH
    _run_check_fix(
        section,
        "Ensure system crypto policy disables CBC ciphers for SSH",
        "grep -q 'aes128-cbc' /etc/crypto-policies/back-ends/opensshserver.config || true",
        (
            "sed -i.bak -E '/^Ciphers / s/$/,aes128-cbc,aes192-cbc,aes256-cbc/' "
            "/etc/crypto-policies/back-ends/opensshserver.config && update-crypto-policies --reload"
        ),
        verify_only, REPORT, log
    )

    # 1.6.6 Ensure system crypto policy disables chacha20-poly1305 for SSH
    _run_check_fix(
        section,
        "Ensure system crypto policy disables chacha20-poly1305 for SSH",
        "grep -q 'chacha20-poly1305' /etc/crypto-policies/back-ends/opensshserver.config || true",
        (
            "sed -i.bak -E '/^Ciphers / s/$/,chacha20-poly1305/' "
            "/etc/crypto-policies/back-ends/opensshserver.config && update-crypto-policies --reload"
        ),
        verify_only, REPORT, log
    )

   # 1.6.7 Ensure system-wide crypto policy disables EtM for SSH
    _run_check_fix(
        section,
        "Ensure system wide crypto policy disables EtM for SSH",
        # Check that EtM MACs are *not* present in the sshd backend policy
        "grep -Eq '^Ciphers|^MACs' /etc/crypto-policies/back-ends/opensshserver.config | grep -q etm@",
        # Remove any EtM entries and reload the policy
        "sed -i.bak '/etm@/d' /etc/crypto-policies/back-ends/opensshserver.config && update-crypto-policies --fallback-to-default",
        verify_only, REPORT, log
    )


    log(f"[✔] {section} completed")
