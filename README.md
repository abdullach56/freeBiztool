# FreeBizTools India

Simple no-login Flask utility site for Indian small businesses and freelancers.

## Features
- GST Calculator (`/gst-calculator`)
- Reverse GST Calculator (`/reverse-gst-calculator`)
- Discount Calculator (`/discount-calculator`)
- Invoice Generator with PDF download (`/invoice-generator`)

### SEO & Ads
- Each page includes dynamic `<title>`, `<meta>` description, canonical link, and structured data (JSON‑LD).
- Base template contains Google AdSense placeholders (`adsbygoogle`) with safe default client/slot IDs.
- Layout and ads are responsive for mobile devices.

## Run locally
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python app.py
```

Open: `http://127.0.0.1:5000`
