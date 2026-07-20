import httpx
import winsound
import time

class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.url = f"https://api.telegram.org/bot{token}/sendMessage"

    def notify(self, message: str) -> bool:
        # FIXME: if telegram is down, this timeout blocks the main loop. 
        # Move to a background thread when I have time to refactor.
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            r = httpx.post(self.url, json=payload, timeout=10.0)
            # print(f"Telegram response: {r.status_code}") # dev debug
            return r.status_code == 200
        except httpx.RequestError:
            # Let the CLI loop keep running even if our internet flickered
            return False

def beep_alert(urgency: str = "normal"):
    """Plays a distinct beep sequence based on urgency level."""
    if urgency == "critical":
        # Rapid high pitched beeps
        for _ in range(5):
            winsound.Beep(1500, 150)
            time.sleep(0.05)
    else: 
        # Standard warning chime
        for _ in range(3):
            winsound.Beep(880, 300)
            time.sleep(0.1)
