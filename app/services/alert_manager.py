from app.services.logger import logger

def send_alert(alert_type: str, details: str):
    logger.critical(
        f"SECURITY ALERT | {alert_type} | {details}"
    )

    return {
        "alert": "generated",
        "type": alert_type,
        "details": details
    }