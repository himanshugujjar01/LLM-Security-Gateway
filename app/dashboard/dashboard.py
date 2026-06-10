from fastapi import APIRouter

router = APIRouter()

@router.get("/logs")
def get_logs():
    try:
        with open("app/logs/security.log", "r") as file:
            logs = file.readlines()

        return {
            "total_logs": len(logs),
            "logs": logs
        }

    except FileNotFoundError:
        return {
            "message": "No logs found"
        }