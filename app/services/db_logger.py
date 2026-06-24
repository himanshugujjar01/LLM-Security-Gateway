from app.database.database import SessionLocal, engine, Base
from app.database.models import PromptLog

Base.metadata.create_all(bind=engine)

def log_prompt_to_db(
    user_message: str,
    redacted_message: str,
    response_text: str,
    status: str,
    detection_type: str
):
    db = SessionLocal()

    try:
        log_entry = PromptLog(
            user_message=user_message,
            redacted_message=redacted_message,
            response_text=response_text,
            status=status,
            detection_type=detection_type
        )

        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)

        return log_entry.id

    finally:
        db.close()