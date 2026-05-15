import json, os
from datetime import datetime

class AuditLogger:
    LOG_FILE = "audit/audit_log.json"

    @staticmethod
    def log(event_type: str, details: dict):
        os.makedirs("audit", exist_ok=True)
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event': event_type,
            'details': details
        }
        logs = []
        if os.path.exists(AuditLogger.LOG_FILE):
            with open(AuditLogger.LOG_FILE, 'r') as f:
                try: logs = json.load(f)
                except: logs = []
        logs.append(entry)
        if len(logs) > 1000: logs = logs[-1000:]
        with open(AuditLogger.LOG_FILE, 'w') as f:
            json.dump(logs, f, indent=2)

    @staticmethod
    def get_logs(limit: int = 100) -> list:
        if not os.path.exists(AuditLogger.LOG_FILE): return []
        with open(AuditLogger.LOG_FILE, 'r') as f:
            try: return json.load(f)[-limit:]
            except: return []