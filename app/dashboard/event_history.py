from fastapi import APIRouter

router = APIRouter()

security_events = []

@router.get("/event-history")
def get_event_history():
    return security_events