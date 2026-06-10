import logging

logging.basicConfig(
    filename="app/logs/security.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("security")