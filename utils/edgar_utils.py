from sec_edgar_downloader import Downloader
from utils.ai_assist import answer_with_code_context  # ✅ clean, refactored
import os
import re

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


def fetch_revenue_from_edgar(ticker: str) -> str:
    """
    Fetches the total annual revenue from the latest 10-K filing for the given ticker symbol.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        str: The total annual revenue reported in the filing, or an error message if it cannot be retrieved.
    """
    try:
        # Step 1: Fetch the latest 10-K filing text
        filing_content = fetch_latest_10k_text(ticker)
        if not filing_content:
            return "No 10-K filing found or unable to fetch content."

        # Step 2: Use regex to extract revenue information
        # Example pattern to match revenue-related phrases and extract the amount
        revenue_pattern = r"(?i)(?:total\s+revenue|net\s+sales)\s*[:\s$]*([\d,]+)"
        match = re.search(revenue_pattern, filing_content)
        if match:
            revenue = match.group(1).replace(",", "")  # Remove commas for a clean number
            return f"Total Revenue: ${revenue}"
        else:
            return "Revenue information could not be found in the 10-K filing."
    except Exception as e:
        return f"Error fetching revenue: {str(e)}"
