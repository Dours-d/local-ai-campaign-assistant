import os
import json
import logging
import datetime
import argparse

# Configuration
LOG_FILE = os.path.join("data", "monitoring.log")
SUMMARY_FILE = os.path.join("data", "health_summary.json")
LOG_LEVEL = logging.INFO
REFRESH_THRESHOLD_MINS = 5 
STALE_THRESHOLD_HOURS = 1 # Flag as 'stale' if log hasn't updated in 1hr
DEGRADED_FAIL_PERCENT = 0.1 # Flag as 'degraded' if fail rate > 10%
DEGRADED_MIN_CHECKS = 5 # Lowered for testing (from 10)
INTEGRITY_SUMMARY = os.path.join("data", "integrity_summary.json")

# Initialize Logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("HealthSnapshot")

def parse_monitor_log():
    """
    Day 1 MVP: Basic parsing of the monitor log to extract uptime and alert metrics.
    """
    logger.info(f"Parsing log file: {LOG_FILE}")
    
    stats = {
        "heartbeat_ok": 0,
        "heartbeat_fail": 0,
        "restart_attempts": 0,
        "restart_success": 0,
        "suppressed_alerts": 0,
        "last_sync": None,
        "system_status": "operational", # operational, stale, degraded
        "status_message": "All systems nominal.",
        "last_update": datetime.datetime.utcnow().isoformat() + "Z"
    }

    if not os.path.exists(LOG_FILE):
        logger.warning(f"Log file {LOG_FILE} not found.")
        return stats

    try:
        with open(LOG_FILE, "r", encoding="utf-8-sig") as f:
            for line in f:
                line_u = line.upper()
                
                # Metrics parsing (non-exclusive)
                if "[OK]" in line_u:
                    stats["heartbeat_ok"] += 1
                
                if "[CRITICAL]" in line_u or "HEARTBEAT_FAILURE" in line_u:
                    if "SKIPPED (COOLDOWN ACTIVE)" not in line_u: # Don't count suppressed as new fail
                        stats["heartbeat_fail"] += 1
                
                if "RESTART_ATTEMPT" in line_u:
                    stats["restart_attempts"] += 1
                
                if "RESTART_SUCCESS" in line_u:
                    stats["restart_success"] += 1
                
                if "SKIPPED (COOLDOWN ACTIVE)" in line_u:
                    stats["suppressed_alerts"] += 1
                
                if "SYSTEM SYNC:" in line_u:
                    stats["last_sync"] = line.split("at")[-1].strip()

        # Phase 6 Enhancements: Visual Integrity Integration
        if os.path.exists(INTEGRITY_SUMMARY):
            try:
                with open(INTEGRITY_SUMMARY, 'r', encoding='utf-8') as f:
                    integrity = json.load(f)
                    stats["visual_integrity"] = integrity.get("status", "unknown")
                    stats["total_pulses"] = integrity.get("total_pulses", 0)
                    stats["missing_assets"] = len(integrity.get("missing_files", []))
                    
                    if integrity.get("status") in ["degraded", "error"]:
                        stats["system_status"] = "degraded"
                        stats["status_message"] = integrity.get("status_message", "Visual Integrity Failure")
            except:
                pass

        # Day 3 Enhancements: Status Flagging
        total_checks = stats["heartbeat_ok"] + stats["heartbeat_fail"]
        
        # 1. Check for stale log (no recent lines)
        if os.path.getsize(LOG_FILE) > 0:
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(LOG_FILE))
            if (datetime.datetime.now() - mtime).total_seconds() > STALE_THRESHOLD_HOURS * 3600:
                stats["system_status"] = "stale"
                stats["status_message"] = f"Warning: No log activity for over {STALE_THRESHOLD_HOURS} hour(s)."
        
        # 2. Check for degraded performance (high fail rate)
        if stats["system_status"] != "stale" and total_checks >= DEGRADED_MIN_CHECKS:
            fail_rate = stats["heartbeat_fail"] / total_checks
            if fail_rate > DEGRADED_FAIL_PERCENT:
                stats["system_status"] = "degraded"
                stats["status_message"] = f"Performance issue: {fail_rate:.1%} heartbeat failure rate detected."

    except Exception as e:
        logger.error(f"Error reading log file: {e}")
        stats["system_status"] = "error"
        stats["status_message"] = f"Internal Error: {str(e)}"

    return stats

def save_summary(stats):
    """
    Saves the aggregated stats to a JSON summary only if the state has changed
    or the forced refresh threshold has been reached.
    """
    try:
        os.makedirs(os.path.dirname(SUMMARY_FILE), exist_ok=True)
        
        # Load existing stats to check for changes
        existing_stats = {}
        if os.path.exists(SUMMARY_FILE):
            try:
                with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
                    existing_stats = json.load(f)
            except:
                pass

        # Check for state changes (ignoring 'last_update')
        state_changed = False
        for key in stats:
            if key != "last_update" and stats.get(key) != existing_stats.get(key):
                state_changed = True
                break
        
        # Check for forced refresh (TTL)
        now = datetime.datetime.utcnow()
        if not state_changed and "last_update" in existing_stats:
            last_upd = datetime.datetime.fromisoformat(existing_stats["last_update"].replace("Z", ""))
            if (now - last_upd).total_seconds() < REFRESH_THRESHOLD_MINS * 60:
                logger.debug("No state change and threshold not met. Skipping write.")
                return False

        with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"Health summary {'updated (state change)' if state_changed else 'refreshed (TTL boundary)'}: {SUMMARY_FILE}")
        return True
    except Exception as e:
        logger.error(f"Failed to save summary: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Generate Health Snapshots from Monitoring Logs")
    parser.add_argument("--verbose", action="store_true", help="Enable detailed drill-down logging")
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled.")

    stats = parse_monitor_log()
    save_summary(stats)

if __name__ == "__main__":
    main()
