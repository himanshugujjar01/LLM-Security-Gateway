from app.services.logger import logger
from app.dashboard.metrics import metrics
from app.dashboard.event_history import security_events
from app.services.email_alert import send_email_alert


def send_alert(alert_type, details):

    security_events.append({
        "event_type": alert_type,
        "details": details
    })

    print(f"[ALERT] {alert_type}: {details}")

    # send email alert
    send_email_alert(alert_type, details)

    return {
        "alert": "generated",
        "type": alert_type,
        "details": details
    }