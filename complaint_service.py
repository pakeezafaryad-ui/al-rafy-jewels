def analyse_complaint(category, subject, message):
    """Deterministic baseline classification; AI enrichment can be added safely later."""
    text = f"{category} {subject} {message}".lower()
    urgent_terms = ["charged twice", "fraud", "payment taken", "missing package", "never arrived"]
    high_terms = ["damaged", "broken", "wrong item", "refund", "allergic", "unsafe"]
    if any(term in text for term in urgent_terms):
        priority = "High"
    elif any(term in text for term in high_terms):
        priority = "Medium"
    else:
        priority = "Normal"
    summary = " ".join((message or "").split())
    if len(summary) > 240:
        summary = summary[:237] + "..."
    return {"priority": priority, "summary": summary or f"{category}: {subject}"}
