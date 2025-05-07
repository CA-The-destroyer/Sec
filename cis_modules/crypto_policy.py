# cis_modules/crypto_policy.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.6 Crypto Policy"

    # 1.6.3 Ensure system-wide crypto policy disables SHA1
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables SHA1",
        "bash -c \"! grep -q sha1 <(update-crypto-policies --show-details)\"",
        "update-crypto-policies --set FUTURE",
        verify_only,
        REPORT,
        log
    )

    # 1.6.5 Ensure system-wide crypto policy disables CBC for SSH
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables CBC for SSH",
        "bash -c \"! grep -q cbc <(update-crypto-policies --show-details)\"",
        "update-crypto-policies --set FUTURE",
        verify_only,
        REPORT,
        log
    )

    # 1.6.6 Ensure system-wide crypto policy disables ChaCha20-Poly1305 for SSH (Manual)
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables ChaCha20-Poly1305 for SSH",
        "true",
        None,
        verify_only,
        REPORT,
        log
    )

    # 1.6.7 Ensure system-wide crypto policy disables EtM for SSH (Manual)
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables EtM for SSH",
        "true",
        None,
        verify_only,
        REPORT,
        log
    )
