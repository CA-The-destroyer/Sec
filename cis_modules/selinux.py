# cis_modules/selinux.py
from cis_modules import _run_check_fix

def run_section(verify_only, REPORT, log):
    section = "1.3 SELinux"
    # 1.3.1.1 Ensure SELinux is installed
    _run_check_fix(section,
                   "Ensure SELinux is installed",
                   "rpm -q selinux-policy-targeted",
                   "yum install -y selinux-policy-targeted",
                   verify_only, REPORT, log)
    # 1.3.1.3 Ensure SELinux policy is configured
    _run_check_fix(section,
                   "Ensure SELinux policy is configured",
                   "grep -q '^SELINUX=enforcing' /etc/selinux/config",
                   "sed -i 's/^SELINUX=.*/SELINUX=enforcing/' /etc/selinux/config",
                   verify_only, REPORT, log)
    # 1.3.1.4 Ensure the SELinux mode is not disabled
    _run_check_fix(section,
                   "Ensure SELinux mode is not disabled",
                   "getenforce | grep -vq Disabled",
                   None,
                   verify_only, REPORT, log)