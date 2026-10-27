from services.complaint_service import analyse_complaint

def test_complaint_priority():
    assert analyse_complaint("Payment issue", "Charged twice", "I was charged twice")["priority"] == "High"
    assert analyse_complaint("Other", "Question", "Can you help?")["priority"] == "Normal"
