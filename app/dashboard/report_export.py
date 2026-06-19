from fastapi import APIRouter
from fastapi.responses import FileResponse
from app.dashboard.metrics import metrics
import csv

router = APIRouter()

@router.get("/export-report")
def export_report():

    filename = "security_report.csv"

    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)

        writer.writerow([
            "Event Type",
            "Count"
        ])

        writer.writerow([
            "Prompt Injections",
            metrics["prompt_injections"]
        ])

        writer.writerow([
            "PII Detections",
            metrics["pii_detected"]
        ])

        writer.writerow([
            "Threat Matches",
            metrics["threat_matches"]
        ])

    return FileResponse(
        filename,
        media_type="text/csv",
        filename=filename
    )