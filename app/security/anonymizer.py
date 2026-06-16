import re

def anonymize_text(text):
    mapping = {}

    phones = re.findall(r'\b\d{10}\b', text)

    for i, phone in enumerate(phones, start=1):
        token = f"[PHONE_{i}]"
        mapping[token] = phone
        text = text.replace(phone, token)

    return text, mapping


def deanonymize_text(text, mapping):
    for token, value in mapping.items():
        text = text.replace(token, value)

    return text