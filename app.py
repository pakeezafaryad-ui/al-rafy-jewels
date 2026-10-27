from pathlib import Path
import streamlit as st
import pandas as pd

from config.settings import BRAND_NAME, TAGLINE
from database.db import init_db, get_products, create_complaint, get_complaints, create_order
from services.email_service import send_complaint_email, send_customer_acknowledgement
from services.product_service import filter_products, get_product_by_id
from services.complaint_service import analyse_complaint
from agents.crew import get_ai_stylist_response
from rag.retriever import answer_with_rag

ROOT = Path(__file__).parent
init_db()

st.set_page_config(page_title=BRAND_NAME, page_icon="💎", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Playfair+Display:wght@500;600&display=swap');
:root { --pink:#F4A7CD; --pink-light:#FCE7EF; --gold:#C5A253; --mauve:#805567; --ivory:#FFF9F5; }
.stApp { background:var(--ivory); color:var(--mauve); }
section[data-testid="stSidebar"] { background:var(--pink-light); }
h1,h2,h3 { font-family:'Playfair Display',serif !important; color:var(--mauve) !important; }
p, label, div, span { font-family:'DM Sans',sans-serif; }
div.stButton > button, div.stFormSubmitButton > button {
 background:var(--gold); color:white; border:0; border-radius:12px;
 font-weight:600; min-height:2.6rem;
}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {
 background:#A98437; color:white; border:0;
}
div[data-testid="stForm"] { background:#FFF0F4; padding:1.1rem; border-radius:16px; }
div[data-testid="stVerticalBlockBorderWrapper"] { border-color:#F1D1DF; border-radius:16px; }
.pill { display:inline-block; padding:5px 12px; border-radius:20px; background:#FCE7EF; color:#805567; font-size:12px; }
.hero { background:linear-gradient(120deg,#FCE7EF,#F4A7CD); padding:30px; border-radius:22px; }
.small-note { color:#805567; font-size:0.88rem; }
</style>
""", unsafe_allow_html=True)

def show_brand_header():
    logo_path = ROOT / "assets" / "images" / "logo.png"
    left, right = st.columns([1, 4], vertical_alignment="center")
    with left:
        if logo_path.exists():
            st.image(str(logo_path), width=150)
        else:
            st.markdown("## 💎")
    with right:
        st.markdown(f"<h1 style='margin-bottom:0'>{BRAND_NAME}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='margin-top:0;color:#9C7540'>{TAGLINE}</p>", unsafe_allow_html=True)
    st.divider()

def add_to_cart(product_id):
    cart = st.session_state.setdefault("cart", {})
    cart[product_id] = cart.get(product_id, 0) + 1

def render_products(products, key_prefix="product"):
    if not products:
        st.info("No products match these filters. Try a different search.")
        return
    cols = st.columns(3)
    for i, p in enumerate(products):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"<div class='pill'>{p['category']}</div>", unsafe_allow_html=True)
                st.markdown(f"### {p['name']}")
                st.write(p["description"])
                st.caption(f"Material: {p['material']} · Stock: {p['stock']}")
                st.markdown(f"**PKR {p['price']:,.0f}**")
                if st.button("Add to bag", key=f"{key_prefix}_{p['id']}"):
                    if p["stock"] <= 0:
                        st.error("This item is currently out of stock.")
                    else:
                        add_to_cart(p["id"])
                        st.success("Added to your bag.")
                        st.rerun()

show_brand_header()

pages = ["Home", "Shop", "AI Jewellery Stylist", "Ask Store Policies", "Customer Complaints", "Shopping Bag", "Admin"]
page = st.radio("Explore", pages, horizontal=True, label_visibility="collapsed")

if page == "Home":
    st.markdown(
        f"<div class='hero'><span class='pill'>JEWELLERY, WITH A PERSONAL TOUCH</span>"
        f"<h1 style='font-size:2.6rem;margin-top:12px'>Find your everyday sparkle.</h1>"
        f"<p>Thoughtfully styled jewellery for gifts, celebrations and the little moments in between.</p>"
        f"</div>", unsafe_allow_html=True
    )
    st.write("")
    st.subheader("Featured collection")
    render_products(get_products(active_only=True)[:6], "home")
    st.caption("Prices and stock shown are sample catalogue data. Update them before accepting real orders.")

elif page == "Shop":
    st.title("Shop the collection")
    products = get_products(active_only=True)
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        search = st.text_input("Search", placeholder="Earrings, pearls, necklace...")
    with c2:
        categories = ["All"] + sorted({p["category"] for p in products})
        category = st.selectbox("Category", categories)
    with c3:
        max_price = st.number_input("Maximum price (PKR)", min_value=0, value=10000, step=500)
    render_products(filter_products(products, search, category, max_price), "shop")

elif page == "AI Jewellery Stylist":
    st.title("Your personal jewellery stylist ✨")
    st.write("Share the occasion, your preferred look and budget. Recommendations use the current catalogue.")
    with st.form("stylist_form"):
        occasion = st.selectbox("Occasion", ["Everyday", "Birthday", "Wedding guest", "Gift", "Formal event"])
        style = st.selectbox("Preferred style", ["Minimal", "Traditional", "Elegant", "Statement", "Surprise me"])
        budget = st.number_input("Budget (PKR)", min_value=0, value=3000, step=500)
        extra = st.text_input("Anything else? (optional)", placeholder="e.g. pearl earrings, gold tone")
        go = st.form_submit_button("Find my jewellery")
    if go:
        products = [p for p in get_products(active_only=True) if p["price"] <= budget and p["stock"] > 0]
        st.subheader("Matching pieces")
        render_products(products[:6], "stylist")
        response = get_ai_stylist_response(occasion, style, budget, extra, products)
        st.markdown("#### Stylist notes")
        st.write(response)

elif page == "Ask Store Policies":
    st.title("Ask Al Rafy")
    st.write("Ask about products, materials, delivery or returns. Answers use the store knowledge files when available.")
    question = st.text_input("Your question", placeholder="What is the return policy?")
    if st.button("Ask") and question.strip():
        st.write(answer_with_rag(question.strip()))

elif page == "Customer Complaints":
    st.title("Customer care 💌")
    st.write("We want to help. Send your concern below and we’ll create a reference number.")
    with st.form("complaint_form", clear_on_submit=True):
        name = st.text_input("Full name")
        email = st.text_input("Email address")
        order_ref = st.text_input("Order reference (optional)")
        category = st.selectbox("Complaint category", [
            "Damaged item", "Incorrect item", "Delivery delay", "Payment issue",
            "Return or refund", "Product quality", "Other"
        ])
        subject = st.text_input("Subject")
        message = st.text_area("Tell us what happened", height=140)
        submit = st.form_submit_button("Submit complaint")
    if submit:
        if not name.strip() or not email.strip() or "@" not in email or "." not in email.split("@")[-1]:
            st.error("Please enter your name and a valid email address.")
        elif not subject.strip() or not message.strip():
            st.error("Please enter a subject and describe your complaint.")
        else:
            analysis = analyse_complaint(category, subject, message)
            complaint_id = create_complaint(
                name.strip(), email.strip(), order_ref.strip(), category,
                subject.strip(), message.strip(), analysis["priority"], analysis["summary"]
            )
            ref = f"ARJ-{complaint_id:06d}"
            owner_result = send_complaint_email(
                ref, name.strip(), email.strip(), order_ref.strip(), category,
                subject.strip(), message.strip(), analysis
            )
            customer_result = send_customer_acknowledgement(
                ref, name.strip(), email.strip(), subject.strip()
            )
            st.success(f"Complaint recorded. Your reference number is **{ref}**.")
            if owner_result:
                st.success("Your complaint notification was emailed to the store.")
            else:
                st.warning("Complaint saved, but the store email could not be confirmed. Please keep your reference number.")
            if customer_result:
                st.info("An acknowledgement email was sent to you.")
            else:
                st.caption("Customer acknowledgement email is not configured or could not be sent.")

elif page == "Shopping Bag":
    st.title("Your shopping bag 🛍️")
    cart = st.session_state.setdefault("cart", {})
    products = {p["id"]: p for p in get_products(active_only=True)}
    total = 0
    if not cart:
        st.info("Your bag is empty. Visit Shop to add something lovely.")
    else:
        for pid in list(cart):
            p = products.get(pid)
            if not p:
                continue
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            c1.write(f"**{p['name']}**")
            qty = c2.number_input("Qty", min_value=1, max_value=max(1, p["stock"]), value=min(cart[pid], max(1, p["stock"])), key=f"qty_{pid}")
            cart[pid] = qty
            c3.write(f"PKR {p['price'] * qty:,.0f}")
            if c4.button("Remove", key=f"remove_{pid}"):
                del cart[pid]
                st.rerun()
            total += p["price"] * qty
        st.divider()
        st.subheader(f"Subtotal: PKR {total:,.0f}")
        st.caption("Shipping and payment are not included. This starter version does not process online payments.")
        with st.form("checkout_form"):
            st.subheader("Request an order")
            customer = st.text_input("Your name")
            customer_email = st.text_input("Email")
            phone = st.text_input("Phone (optional)")
            address = st.text_area("Delivery address")
            place_order = st.form_submit_button("Submit order request")
        if place_order:
            if not customer.strip() or "@" not in customer_email or not address.strip():
                st.error("Enter your name, a valid email and delivery address.")
            else:
                order_items = [{"product_id": pid, "name": products[pid]["name"], "quantity": qty,
                                "unit_price": products[pid]["price"]} for pid, qty in cart.items() if pid in products]
                order_id = create_order(customer.strip(), customer_email.strip(), phone.strip(), address.strip(), order_items, total)
                st.success(f"Order request saved: **ARJ-ORD-{order_id:06d}**. The store must confirm availability and payment separately.")
                st.session_state.cart = {}
                st.rerun()

elif page == "Admin":
    st.title("Store admin")
    st.warning("Demo admin view: protect this page with proper authentication before public launch.")
    expected = st.secrets.get("ADMIN_PASSWORD", "") if hasattr(st, "secrets") else ""
    password = st.text_input("Admin password", type="password")
    if expected and password and password == expected:
        st.success("Admin access granted.")
        complaints = get_complaints()
        if complaints:
            st.dataframe(pd.DataFrame(complaints), use_container_width=True)
        else:
            st.info("No complaints recorded yet.")
    elif not expected:
        st.info("Set ADMIN_PASSWORD in Streamlit secrets to enable this demo gate.")
    elif password:
        st.error("Incorrect password.")

st.divider()
st.markdown(
    f"<p style='text-align:center;color:#9C7540'>💗 {BRAND_NAME} · {TAGLINE}</p>",
    unsafe_allow_html=True
)
