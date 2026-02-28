import os
import re
import json
import logging

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
LOG_FILE = os.path.join(DATA_DIR, "monitoring.log")
SUMMARY_FILE = os.path.join(DATA_DIR, "health_summary.json")

# Regex Patterns for PII
RE_PHONE = re.compile(r'\+?[1-9]\d{9,14}') # Must be at least 10 digits
RE_WALLET = re.compile(r'0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}') # ETH/BTC wallets

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger("PrivacyAudit")

def audit_file(file_path, patterns):
    """Scans a file for PII patterns."""
    found_pii = []
    if not os.path.exists(file_path):
        return found_pii

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                for name, pattern in patterns.items():
                    matches = pattern.findall(line)
                    if matches:
                        # Mask the matches for the report
                        masked = [m[:4] + "****" + m[-4:] if len(m) > 8 else "****" for m in matches]
                        found_pii.append({
                            "file": os.path.basename(file_path),
                            "line": i,
                            "type": name,
                            "matches": masked
                        })
    except Exception as e:
        logger.error(f"Error auditing {file_path}: {e}")
    
    return found_pii

def audit_json_summary():
    """Ensures health_summary.json is clean."""
    if not os.path.exists(SUMMARY_FILE):
        return True
    
    try:
        with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Check all values for PII
            flat_data = str(data)
            for name, pattern in {"PHONE": RE_PHONE, "WALLET": RE_WALLET}.items():
                if pattern.search(flat_data):
                    logger.warning(f"PII Leak detected in {SUMMARY_FILE}!")
                    return False
    except Exception as e:
        logger.error(f"Error auditing JSON summary: {e}")
    
    return True

def audit_scripts_for_unsafe_logging():
    """Scans Python scripts for print(pii) or logging.info(pii)."""
    # Refined to avoid matching 'len(...)', 'count', or 'index'
    unsafe_patterns = {
        "UNSAFE_PRINT": re.compile(r'print\(.*(?<!len\()(?<!count)(?<!index)(phone|wallet|beneficiary_id).*\)'),
        "UNSAFE_LOG": re.compile(r'log.*\(.*(?<!len\()(?<!count)(?<!index)(phone|wallet|beneficiary_id).*\)')
    }
    
    issues = []
    for root, _, files in os.walk(SCRIPTS_DIR):
        for file in files:
            if file.endswith(".py") and file != "audit_privacy_compliance.py":
                path = os.path.join(root, file)
                issues.extend(audit_file(path, unsafe_patterns))
    return issues

def main():
    logger.info("Starting Privacy & Compliance Audit...")
    
    # 1. Audit Public Logs
    pii_in_logs = audit_file(LOG_FILE, {"PHONE": RE_PHONE, "WALLET": RE_WALLET})
    
    # 2. Audit JSON Summary
    summary_clean = audit_json_summary()
    
    # 3. Audit Codebase for unsafe logging
    code_issues = audit_scripts_for_unsafe_logging()
    
    # Report results
    if not pii_in_logs and summary_clean and not code_issues:
        logger.info("✅ Audit PASSED. No PII leaks or unsafe logging patterns found.")
    else:
        logger.warning("❌ Audit FAILED. Issues found:")
        for issue in pii_in_logs + code_issues:
            logger.warning(f"  - {issue['file']}:{issue['line']} | {issue['type']} | Found: {issue['matches']}")
        if not summary_clean:
            logger.warning(f"  - {os.path.basename(SUMMARY_FILE)} contains potential PII data.")

if __name__ == "__main__":
    main()
