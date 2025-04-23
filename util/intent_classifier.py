# intent_classifier.py

import re

intent_keywords = {
    "report_summary": ["spending", "how much", "summary", "ratio"],
    "adjust_category_forecast": ["increase", "decrease", "reduce", "raise", "adjust"],
    "recommend_action": ["recommend", "suggest", "how can I", "save money", "lower costs"],
    "show_risk_insight": ["risk", "at risk", "protect", "exposure"],
    "optimize_margin": ["margin", "improve margin", "profit"]
}

def classify_intent(prompt):
    for intent, keywords in intent_keywords.items():
        for keyword in keywords:
            if re.search(rf"\\b{re.escape(keyword)}\\b", prompt.lower()):
                return intent
    return "unknown"

intent_keywords = {
    "report_summary": ["spending", "how much", "summary", "ratio"],
    "adjust_category_forecast": ["increase", "decrease", "reduce", "raise", "adjust"],
    "recommend_action": ["recommend", "suggest", "how can I", "save money", "lower costs"],
    "show_risk_insight": ["risk", "at risk", "protect", "exposure"],
    "optimize_margin": ["margin", "improve margin", "profit"],
    "analyze_product": ["compare", "alternative", "better than", "replace", "product", "option", "upgrade"]
}
