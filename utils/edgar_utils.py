from sec_edgar_downloader import Downloader
import os
import re

def fetch_latest_10k_text(ticker: str) -> str:
    """
    Fetches the latest 10-K filing for the given ticker symbol from the SEC EDGAR database.
    """
    try:
        dl = Downloader()
        dl.get("10-K", ticker.upper(), amount=1)

        path = os.path.join("SEC-Edgar-Data", ticker.upper())
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".txt") or file.endswith(".html"):
                    with open(os.path.join(root, file), encoding="utf-8") as f:
                        return f.read()

        return "No 10-K filing found for the given ticker."
    except Exception as e:
        return f"Error fetching 10-K filing: {str(e)}"


def fetch_revenue_from_edgar(ticker: str) -> str:
    """
    Extracts total annual revenue from the latest 10-K filing.
    """
    try:
        filing_content = fetch_latest_10k_text(ticker)
        if not filing_content:
            return "No 10-K filing found or unable to fetch content."

        revenue_pattern = r"(?i)(?:total\s+revenue|net\s+sales)\s*[:\s$]*([\d,]+)"
        match = re.search(revenue_pattern, filing_content)

        if match:
            revenue = match.group(1).replace(",", "")
            return f"Total Revenue: ${revenue}"
        else:
            return "Revenue information could not be found in the 10-K filing."
    except Exception as e:
        return f"Error fetching revenue: {str(e)}"
