# LLM Security Gateway

## Overview

LLM Security Gateway is a FastAPI-based security layer designed to protect Large Language Model (LLM) applications from common security threats such as Prompt Injection attacks, Personally Identifiable Information (PII) leakage, and unauthorized API access.

The gateway inspects incoming requests, detects malicious prompts, redacts sensitive data, logs security events, and provides a dashboard for monitoring security incidents.

---

## Features

### Prompt Injection Detection

* Detects common prompt injection patterns.
* Blocks malicious requests before reaching the LLM.
* Logs all detected injection attempts.

### PII Detection and Redaction

* Detects and redacts:

  * Email Addresses
  * Phone Numbers
  * Aadhaar Numbers
  * Credit Card Numbers
* Prevents sensitive data exposure.

### API Key Authentication

* Secures endpoints using API key verification.
* Blocks unauthorized access.

### Security Logging

* Records security events in `security.log`.
* Tracks:

  * Prompt Injection Attempts
  * PII Detections
  * Request Processing Events

### Security Dashboard

* Provides real-time security statistics.
* Displays:

  * Total Security Events
  * Prompt Injection Attempts

### Rate Limiting

* Protects APIs against abuse and excessive requests.

---

## Project Structure

```text
app/
├── auth/
│   └── api_key.py
├── dashboard/
│   └── dashboard.py
├── logs/
│   └── security.log
├── middleware/
│   └── rate_limiter.py
├── security/
│   ├── pii_detector.py
│   ├── prompt_injection.py
│   └── output_filter.py
├── services/
│   └── logger.py
├── config.py
└── main.py
```

## Installation

### Clone Repository

```bash
git clone <repository-url>
cd llm-security-gateway
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
uvicorn app.main:app --reload
```

Application will start at:

```text
http://127.0.0.1:8000
```

Swagger Documentation:

```text
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### Chat Endpoint

```http
POST /chat
```

Headers:

```text
x-api-key: my-secret-key
```

Request:

```json
{
  "message": "My email is user@example.com"
}
```

Response:

```json
{
  "original": "My email is user@example.com",
  "redacted": "My email is [EMAIL]"
}
```

---

### Security Statistics

```http
GET /stats
```

Response:

```json
{
  "total_events": 10,
  "prompt_injections": 2
}
```
 Automated Incident Containment

### Features
- Detects prompt injection attacks
- Automatically triggers containment action
- Simulates host isolation
- Logs security incidents

### Example Response

{
  "status": "blocked",
  "reason": "Prompt Injection Attempt Detected",
  "containment": {
    "status": "isolated",
    "hostname": "PC-001",
    "action": "network containment executed"
  }
}

## Threat Intelligence Detection

The gateway checks incoming prompts against a threat intelligence feed containing known malicious keywords.

### Current Indicators
- malware
- ransomware
- keylogger
- steal credentials
- bypass security
---

## Security Workflow

1. User sends request.
2. API Key is validated.
3. Prompt Injection Detection runs.
4. PII Detection and Redaction runs.
5. Output Filtering runs.
6. Security Events are logged.
7. Sanitized response is returned.

---

## Technologies Used

* Python
* FastAPI
* Uvicorn
* Regular Expressions (Regex)
* Logging Module

---

## Future Enhancements

* JWT Authentication
* Redis-based Rate Limiting
* Threat Intelligence Integration
* Grafana Dashboard
* Machine Learning-based Prompt Injection Detection
* SIEM Integration

---

## Author

Himanshu

Cybersecurity Intern Project
LLM Security Gateway
