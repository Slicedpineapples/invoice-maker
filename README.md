# Invoice Maker

Professional PDF invoice generator using Python + Jinja2 + WeasyPrint.

## Requirements

- Python 3.10+
- Homebrew (macOS) — for system dependencies

## Setup

**1. Install system dependencies (macOS)**

```bash
brew install pango
```

**2. Create a virtual environment and install Python packages**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**3. Configure your company details**

Create a `.env` file in the project root:

```env
COMPANY_NAME=Your Company Ltd.
COMPANY_ADDRESS=123 Business Street
COMPANY_CITY=London, EC1A 1BB
COMPANY_COUNTRY=United Kingdom
COMPANY_EMAIL=billing@yourcompany.com
COMPANY_BANK_NAME=Barclays Bank
COMPANY_BANK_ACCOUNT=12-34-56 / 87654321

# Optional
COMPANY_PHONE=+44 20 1234 5678
COMPANY_VAT_NUMBER=GB123456789
COMPANY_BANK_IBAN=GB29 NWBK 6016 1331 9268 19
COMPANY_BANK_SWIFT=BARCGB22
```

Your seller/company details are loaded from `.env` automatically. You only need to set this once.

## Usage

```bash
# Generate from the sample invoice
python app.py

# Generate from your own invoice file
python app.py data/my_invoice.json

# Specify a custom output path
python app.py data/my_invoice.json -o output/acme_march.pdf
```

PDFs are saved to `output/` by default, named after the invoice number.

## Invoice JSON format

Each invoice is a JSON file in `data/`. The `seller` block is optional — if omitted, it is loaded from `.env`.

```json
{
  "invoice_number": "INV-001",
  "date": "2026-03-19",
  "due_date": "2026-04-02",
  "payment_terms": "Net 14",

  "client": {
    "name": "Client Company Inc.",
    "address": "456 Client Avenue",
    "city": "New York, NY 10001",
    "country": "United States",
    "email": "accounts@clientcompany.com",
    "vat_number": "US987654321"
  },

  "items": [
    { "description": "Web Design", "quantity": 1, "unit_price": 2500.00 },
    { "description": "Hosting (months)", "quantity": 3, "unit_price": 150.00 }
  ],

  "tax_rate": 20,
  "currency": "GBP",
  "currency_symbol": "£",
  "notes": "Payment by bank transfer. Please include the invoice number as reference."
}
```

## Project structure

```
invoice-maker/
├── app.py                  ← generator script
├── requirements.txt
├── .env                    ← your company details (not committed)
├── logo.png                ← your company logo
├── templates/
│   └── invoice.html        ← Jinja2 template (edit to change design)
├── data/
│   └── sample_invoice.json ← example invoice
└── output/
    └── INV-001.pdf         ← generated PDFs land here
```

## Customising the design

Open [templates/invoice.html](templates/invoice.html) and change the CSS variable at the top:

```css
:root { --accent: #1a1a2e; }
```

That single colour controls the header bar, table header, total row, and divider — one change rebrands the whole invoice.
