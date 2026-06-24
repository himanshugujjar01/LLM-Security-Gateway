from app.services.logger import logger
from app.dashboard.event_history import security_events
from app.services.email_alert import send_email_alert
from app.services.containment import isolate_host


def send_alert(alert_type, details):

    security_events.append({
        "event_type": alert_type,
        "details": details
    })

    print(f"[ALERT] {alert_type}: {details}")

    # Send email alert
    send_email_alert(alert_type, details)

    containment_result = None

    # Auto containment for critical alerts
    if alert_type in ["PROMPT_INJECTION", "THREAT_INTEL_MATCH"]:
        containment_result = isolate_host("LLM Gateway")

        security_events.append({
            "event_type": "CONTAINMENT_ACTION",
            "details": containment_result
        })

    return {
        "alert": "generated",
        "type": alert_type,
        "details": details,
        "containment": containment_result
    }