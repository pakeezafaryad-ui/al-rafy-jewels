# Al Rafy Jewels

A Streamlit jewellery storefront starter with a baby-pink and gold theme, product catalogue, shopping bag, complaint centre, optional Groq stylist, knowledge-base retrieval and SQLite persistence.

## Features
- Streamlit storefront and catalogue search/filtering
- SQLite product, complaint and order-request storage
- Complaint reference numbers and optional Resend notifications
- Optional Groq-powered jewellery stylist
- Store-policy knowledge documents and retrieval fallback
- Optional FAISS index builder
- Starter n8n webhook workflow
- Sample tests

## Important before launch
The catalogue contains sample products, prices and stock. Shipping and return documents are drafts. Review all business details before accepting real orders. Online payments, courier integrations, customer accounts and production-grade admin authentication are not implemented in this starter.

## Local setup
Python 3.10 or 3.11 is recommended.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

The SQLite database is created automatically in `database/store.db` on first run. This file is local runtime data and is ignored by Git.

## Streamlit Cloud
1. Push this repository to GitHub.
2. Create an app at https://share.streamlit.io/.
3. Select this repository and `app.py`.
4. Add secrets in App settings → Secrets, using `.streamlit/secrets.toml.example` as a guide.
5. Set `RESEND_API_KEY`, `OWNER_EMAIL` and a verified `SENDER_EMAIL` to enable email.
6. Set `GROQ_API_KEY` to enable Groq stylist responses.
7. Set `ADMIN_PASSWORD` to enable the simple demo password gate.

Do not commit real API keys. Resend email delivery requires a valid account and configured sender. The app only reports email success when the provider call succeeds.

## Logo
The supplied brand logo should be uploaded to `assets/images/logo.png`. Keep the exact filename and path.

## RAG indexing (optional)
The current app uses a simple keyword retrieval fallback. To create a local FAISS index from the knowledge-base Markdown files:

```bash
python -m rag.ingest
```

The index is generated under `rag/index/` and is ignored by Git. The current starter does not automatically load the FAISS index into app responses yet.

## n8n (optional)
Import `n8n/complaint_workflow.json` into n8n. The starter workflow validates and normalises a webhook payload but does not send email yet. Configure webhook authentication and add your preferred email node before activating it. Avoid enabling both Python and n8n to send the same email.

## Tests
Install pytest (`pip install pytest`) and run:

```bash
pytest -q
```

## Production checklist
- Replace sample catalogue data with accurate products and stock.
- Review shipping, returns, privacy and customer-service policies.
- Add proper authentication and authorisation for admin actions.
- Use managed persistent database and storage for production deployment.
- Add CSRF/spam protection and rate limiting to public forms.
- Implement a real payment gateway before advertising online payment.
- Test email delivery, secrets, database persistence and all customer flows.
