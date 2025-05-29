# cis_modules/crypto_policy.py

from cis_modules import _run_check_fix


def run_section(verify_only, REPORT, log):
    section = "1.6 Configure system-wide crypto policy"

    # 1.6.1 Ensure system wide crypto policy is not set to legacy
    _run_check_fix(
        section,
        "Ensure crypto policy is not set to LEGACY",
        "update-crypto-policies --show | grep -qv 'LEGACY'",
        "update-crypto-policies --set DEFAULT",
        verify_only, REPORT, log
    )

    # 1.6.3 Ensure system wide crypto policy disables sha1 hash and signature support
    _run_check_fix(
        section,
        "Ensure SHA1 is disabled in crypto policy",
        "grep -q 'sha1' /etc/crypto-policies/back-ends/opensshserver.config",
        (
            "update-crypto-policies --set DEFAULT:!SHA1 && "
            "update-crypto-policies --reload"
        ),
        verify_only, REPORT, log
    )

    # 1.6.5 Ensure system wide crypto policy disables CBC for SSH
    _run_check_fix(
        section,
        "Ensure CBC ciphers are disabled for SSH",
        "grep -q 'Ciphers.*cbc' /etc/crypto-policies/back-ends/opensshserver.config",
        (
            "update-crypto-policies --set DEFAULT:!CBC && "
            "update-crypto-policies --reload"
        ),
        verify_only, REPORT, log
    )

    # 1.6.6 Ensure system wide crypto policy disables chacha20-poly1305 for SSH
    _run_check_fix(
        section,
        "Ensure chacha20-poly1305 is disabled for SSH",
        "grep -q 'chacha20-poly1305' /etc/crypto-policies/back-ends/opensshserver.config",
        (
            "update-crypto-policies --set DEFAULT:!CHACHA20-POLY1305 && "
            "update-crypto-policies --reload"
        ),
        verify_only, REPORT, log
    )

    # 1.6.7 Ensure system wide crypto policy disables EtM for SSH
    _run_check_fix(
        section,
        "Ensure EtM is disabled for SSH",
        "grep -q 'EtM' /etc/crypto-policies/back-ends/opensshserver.config",
        (
            "update-crypto-policies --set DEFAULT:!EtM && "
            "update-crypto-policies --reload"
        ),
        verify_only, REPORT, log
    )

    log(f"[✔] {section} completed")
