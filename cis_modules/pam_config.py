# cis_modules/pam_config.py

from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "5.3 PAM Configuration"
    pam_file = "/etc/pam.d/password-auth"

    #
    # 5.3.3.2.1 Ensure number of changed characters (difok) configured
    #
    _run_check_fix(
        section,
        "Ensure pam_pwquality difok=3 is configured",
        "grep -E 'pam_pwquality.so.*difok=[0-9]+' {} | grep -q 'difok=3'".format(pam_file),
        "sed -i '/pam_pwquality.so/s/$/ difok=3/' {}".format(pam_file),
        verify_only, REPORT, log
    )

    #
    # 5.3.3.2.2 Ensure password length (minlen) configured
    #
    _run_check_fix(
        section,
        "Ensure pam_pwquality minlen=14 is configured",
        "grep -E 'pam_pwquality.so.*minlen=[0-9]+' {} | grep -q 'minlen=14'".format(pam_file),
        "sed -i '/pam_pwquality.so/s/$/ minlen=14/' {}".format(pam_file),
        verify_only, REPORT, log
    )

    #
    # 5.3.3.3.1 Ensure password history remember=5 is configured
    #
    _run_check_fix(
        section,
        "Ensure pam_pwhistory remember=5 is configured",
        "grep -E 'pam_pwhistory.so.*remember=[0-9]+' {} | grep -q 'remember=5'".format(pam_file),
        "sed -i '/pam_pwhistory.so/s/$/ remember=5/' {}".format(pam_file),
        verify_only, REPORT, log
    )

    #
    # 5.3.3.4.1 Ensure pam_unix does not include nullok
    #
    _run_check_fix(
        section,
        "Ensure pam_unix does not include nullok",
        "grep -E 'pam_unix.so' {} | grep -vq 'nullok'".format(pam_file),
        "sed -i '/pam_unix.so/s/nullok//g' {}".format(pam_file),
        verify_only, REPORT, log
    )
