from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def presidio_redact(text: str):
    results = analyzer.analyze(
        text=text,
        language="en"
    )

    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=results
    )

    return {
        "original": text,
        "redacted": anonymized_result.text,
        "entities_found": [
            result.entity_type for result in results
        ]
    }