from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.6 Crypto Policy"

    # Ensure system-wide crypto policy is set to DEFAULT (not LEGACY)
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy is not set to LEGACY",
        "update-crypto-policies --show | grep -qv legacy",
        "update-crypto-policies --set DEFAULT",
        verify_only, REPORT, log
    )

    # Ensure SHA1 is disabled
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables sha1 hash and signature support",
        "update-crypto-policies --show | grep -q ':!SHA1'",
        "update-crypto-policies --set DEFAULT:!SHA1 && update-crypto-policies --reload",
        verify_only, REPORT, log
    )

    # Ensure CBC for SSH is disabled
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables cbc for ssh",
        "grep -q 'Ciphers.*-aes128-cbc' /etc/crypto-policies/back-ends/openssh.config",
        "echo 'Ciphers -aes128-cbc' >> /etc/crypto-policies/back-ends/openssh.config && update-crypto-policies --reload",
        verify_only, REPORT, log
    )

    # Ensure chacha20-poly1305 for SSH is disabled
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables chacha20-poly1305 for ssh",
        "grep -q 'Ciphers.*-chacha20-poly1305@openssh.com' /etc/crypto-policies/back-ends/openssh.config",
        "echo 'Ciphers -chacha20-poly1305@openssh.com' >> /etc/crypto-policies/back-ends/openssh.config && update-crypto-policies --reload",
        verify_only, REPORT, log
    )

    # Ensure EtM for SSH is disabled
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables EtM for ssh",
        "grep -q 'MACs.*-hmac-etm' /etc/crypto-policies/back-ends/openssh.config",
        "echo 'MACs -hmac-etm' >> /etc/crypto-policies/back-ends/openssh.config && update-crypto-policies --reload",
        verify_only, REPORT, log
    )
