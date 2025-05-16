# cis_modules/crypto_policy.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.6 Crypto Policy"

    #
    # 1.6.3 Ensure system-wide crypto policy disables SHA1 in TLS back-ends
    #
    # We target only OpenSSL and GnuTLS policy files, not openssh.config.
    tls_files = "/etc/crypto-policies/back-ends/openssl.config " \
                "/etc/crypto-policies/back-ends/gnutls.config"
    check_sha1 = f"! grep -Riq 'sha1' {tls_files}"
    fix_sha1 = (
        f"grep -Rl 'sha1' {tls_files} | xargs -r sed -i '/sha1/Id' && "
        "update-crypto-policies --reload"
    )
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables SHA1 in TLS back-ends",
        check_sha1,
        fix_sha1,
        verify_only, REPORT, log
    )

    #
    # 1.6.5 Ensure system-wide crypto policy disables AES-CBC ciphers for SSH
    #
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables AES-CBC for SSH",
        "grep -q 'Ciphers.*-aes128-cbc' /etc/crypto-policies/back-ends/openssh.config",
        "echo 'Ciphers -aes128-cbc' >> /etc/crypto-policies/back-ends/openssh.config && update-crypto-policies --reload",
        verify_only, REPORT, log
    )

    #
    # 1.6.6 Ensure system-wide crypto policy disables chacha20-poly1305@openssh.com for SSH
    #
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables chacha20-poly1305 for SSH",
        "grep -q 'Ciphers.*-chacha20-poly1305@openssh.com' /etc/crypto-policies/back-ends/openssh.config",
        "echo 'Ciphers -chacha20-poly1305@openssh.com' >> /etc/crypto-policies/back-ends/openssh.config && update-crypto-policies --reload",
        verify_only, REPORT, log
    )

    #
    # 1.6.7 Ensure system-wide crypto policy disables EtM (encrypt-then-MAC) for SSH
    #
    _run_check_fix(
        section,
        "Ensure system-wide crypto policy disables EtM for SSH",
        "grep -q 'MACs.*-hmac-etm' /etc/crypto-policies/back-ends/openssh.config",
        "echo 'MACs -hmac-etm' >> /etc/crypto-policies/back-ends/openssh.config && update-crypto-policies --reload",
        verify_only, REPORT, log
    )
