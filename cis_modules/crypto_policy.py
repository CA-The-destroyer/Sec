# cis_modules/crypto_policy.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.6 Crypto Policy"

    #
    # 1.6.3 Ensure system-wide crypto policy disables SHA1
    #
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables SHA1",
        "update-crypto-policies --show | grep -q ':!SHA1'",
        "update-crypto-policies --set DEFAULT:!SHA1 && update-crypto-policies --reload",
        verify_only, REPORT, log
    )

    #
    # 1.6.5 Ensure system-wide crypto policy disables CBC for SSH
    #
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables CBC ciphers for SSH",
        "grep -q 'Ciphers.*-aes128-cbc' /etc/crypto-policies/back-ends/openssh.config",
        "echo 'Ciphers -aes128-cbc' >> /etc/crypto-policies/back-ends/openssh.config && update-crypto-policies --reload",
        verify_only, REPORT, log
    )

    #
    # 1.6.6 Ensure system-wide crypto policy disables chacha20-poly1305 for SSH
    #
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables chacha20-poly1305 for SSH",
        "grep -q 'Ciphers.*-chacha20-poly1305@openssh.com' /etc/crypto-policies/back-ends/openssh.config",
        "echo 'Ciphers -chacha20-poly1305@openssh.com' >> /etc/crypto-policies/back-ends/openssh.config && update-crypto-policies --reload",
        verify_only, REPORT, log
    )

    #
    # 1.6.7 Ensure system-wide crypto policy disables EtM for SSH
    #
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables EtM for SSH",
        "grep -q 'MACs.*-hmac-etm' /etc/crypto-policies/back-ends/openssh.config",
        "echo 'MACs -hmac-etm' >> /etc/crypto-policies/back-ends/openssh.config && update-crypto-policies --reload",
        verify_only, REPORT, log
    )
