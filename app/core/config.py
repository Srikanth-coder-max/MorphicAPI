import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        target_url = os.getenv("TARGET_VENDOR_URL")
        if not target_url:
            raise ValueError(
                "CRITICAL ERROR: TARGET_VENDOR_URL is missing from my .env file."
                "The server cannot start without target vendor destination."
            )
        self.TARGET_VENDOR_URL: str = target_url

settings = Settings()