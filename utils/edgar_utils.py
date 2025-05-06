from sec_edgar_downloader import Downloader
from utils.ai_assist import answer_with_code_context  # ✅ clean, refactored
import os

def fetch_latest_10k_text(ticker: str) -> str:
    dl = Downloader()
    dl.get("10-K", ticker.upper(), amount=1)

    path = os.path.join("SEC-Edgar-Data", ticker.upper())
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith(".txt") or file.endswith(".html"):
                with open(os.path.join(root, file), encoding="utf-8") as f:
                    return f.read()
    return ""
