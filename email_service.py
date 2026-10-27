import streamlit as st
import resend
from database.db import mark_complaint_email

def _secret(name, default=""):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default

def _send(to, subject, html):
    api_key = _secret("RESEND_API_KEY", "")
    sender = _secret("SENDER_EMAIL", "")
    if not api_key or not sender or not to:
        return False
    try:
        resend.api_key = api_key
        resend.Emails.send({
            "from": sender,
            "to": [to],
            "subject": subject,
            "html": html
        })
        return True
    except Exception:
        return False

def send_complaint_email(ref, name, email, order_ref, category, subject, message, analysis):
    owner = _secret("OWNER_EMAIL", "")
    html = f"""
    <h2>New Al Rafy Jewels complaint</h2>
    <p><b>Reference:</b> {ref}</p>
    <p><b>Customer:</b> {name}</p>
    <p><b>Email:</b> {email}</p>
    <p><b>Order reference:</b> {order_ref or 'Not provided'}</p>
    <p><b>Category:</b> {category}</p>
    <p><b>Priority:</b> {analysis['priority']}</p>
    <p><b>Subject:</b> {subject}</p>
    <p><b>Message:</b><br>{message}</p>
    """
    success = _send(owner, f"[{ref}] {analysis['priority']} complaint: {subject}", html)
    try:
        complaint_id = int(ref.split("-")[-1])
        mark_complaint_email(complaint_id, owner_sent=success)
    except Exception:
        pass
    return success

def send_customer_acknowledgement(ref, name, email, subject):
    html = f"""
    <p>Hello {name},</p>
    <p>Thank you for contacting Al Rafy Jewels about: <b>{subject}</b>.</p>
    <p>Your complaint reference is <b>{ref}</b>. Our team will review your message.</p>
    <p>This is an acknowledgement, not a confirmation that a refund or other action has been approved.</p>
    <p>Regards,<br>Al Rafy Jewels Customer Care</p>
    """
    success = _send(email, f"We received your message ({ref})", html)
    try:
        complaint_id = int(ref.split("-")[-1])
        mark_complaint_email(complaint_id, customer_sent=success)
    except Exception:
        pass
    return success
