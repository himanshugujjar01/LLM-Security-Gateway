import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email_alert(alert_type, details):
    sender_email = "himanshuthurgla@gmail.com"
    sender_password = "zjbu nsrj xsez feoa"
    receiver_email = "himanshuthurgla@gmail.com"   # you can keep same for testing

    subject = f"LLM Security Alert: {alert_type}"
    body = f"""
Security Alert Triggered

Type: {alert_type}
Details: {details}
"""

    try:
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject

        message.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()

        print("[EMAIL ALERT SENT]")
        return {"email": "sent"}

    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return {"email": "failed", "error": str(e)}