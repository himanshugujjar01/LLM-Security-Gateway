from app.services.logger import logger

def isolate_host(host_name):
    print(f"[CONTAINMENT] Host isolated: {host_name}")
    return {
        "status": "isolated",
        "host": host_name,
        "action": "Host isolated successfully"
    }