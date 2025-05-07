# cis_modules/crypto_policy.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.6 Crypto Policy"

    # 1.6.3 Ensure SHA1 disabled
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables SHA1",
        "update-crypto-policies --show-details | grep -q sha1 && exit 1 || exit 0",
        "update-crypto-policies --set FUTURE",
        verify_only, REPORT, log
    )

    # 1.6.5 Ensure CBC disabled for SSH
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables CBC for SSH",
        "update-crypto-policies --show-details | grep -q cbc && exit 1 || exit 0",
        "update-crypto-policies --set FUTURE",
        verify_only, REPORT, log
    )

    # 1.6.6 Ensure ChaCha20-Poly1305 disabled for SSH (Manual)
    _run_check_fix(
        section,
        "Ensure ChaCha20-Poly1305 is disabled for SSH",
        "true",
        None,
        verify_only, REPORT, log
    )

    # 1.6.7 Ensure EtM disabled for SSH (Manual)
    _run_check_fix(
        section,
        "Ensure EtM is disabled for SSH",
        "true",
        None,
        verify_only, REPORT, log
    )
