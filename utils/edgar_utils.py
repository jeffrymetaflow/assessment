from sec_edgar_downloader import Downloader
from utils.ai_assist import answer_with_code_context  # ✅ clean, refactored
import os

def fetch_latest_10k_text(ticker: str) -> str:
    """
    Fetches the latest 10-K filing for the given ticker symbol from the SEC EDGAR database.

    Args:
        ticker (str): The stock ticker symbol for the company.

    Returns:
        str: The content of the latest 10-K filing, or an error message if the filing cannot be retrieved.
    """
    try:
        # Initialize the downloader
        dl = Downloader()
        dl.get("10-K", ticker.upper(), amount=1)

        # Define the expected download path
        path = os.path.join("SEC-Edgar-Data", ticker.upper())
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".txt") or file.endswith(".html"):
                    with open(os.path.join(root, file), encoding="utf-8") as f:
                        return f.read()

        # If no matching file is found
        return "No 10-K filing found for the given ticker."
    except Exception as e:
        return f"Error fetching 10-K filing: {str(e)}"
