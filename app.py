#!/usr/bin/env python3
"""
Invoice Maker
-------------
Usage:
    python app.py                          # generate from data/sample_invoice.json
    python app.py data/my_invoice.json     # generate from a custom JSON file
    python app.py data/my_invoice.json -o output/custom_name.pdf
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

load_dotenv()


BASE_DIR = Path(__file__).parent.resolve()
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"
LOGO_PATH = BASE_DIR / "logo.png"


def load_invoice(json_path: Path) -> dict:
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def load_seller_from_env() -> dict:
    seller = {
        "name": os.environ["COMPANY_NAME"],
        "address": os.environ["COMPANY_ADDRESS"],
        "city": os.environ["COMPANY_CITY"],
        "country": os.environ["COMPANY_COUNTRY"],
        "email": os.environ["COMPANY_EMAIL"],
        "bank_name": os.environ["COMPANY_BANK_NAME"],
        "bank_account": os.environ["COMPANY_BANK_ACCOUNT"],
    }
    for key, env_var in [
        ("phone", "COMPANY_PHONE"),
        ("vat_number", "COMPANY_VAT_NUMBER"),
        ("bank_iban", "COMPANY_BANK_IBAN"),
        ("bank_swift", "COMPANY_BANK_SWIFT"),
    ]:
        value = os.environ.get(env_var)
        if value:
            seller[key] = value
    return seller


def validate(data: dict) -> None:
    required_top = ["invoice_number", "date", "due_date", "seller", "client", "items"]
    for field in required_top:
        if field not in data:
            raise ValueError(f"Missing required field: '{field}'")

    required_seller = ["name", "address", "city", "country", "email",
                       "bank_name", "bank_account"]
    for field in required_seller:
        if field not in data["seller"]:
            raise ValueError(f"Missing required seller field: '{field}'")

    required_client = ["name", "address", "city", "country"]
    for field in required_client:
        if field not in data["client"]:
            raise ValueError(f"Missing required client field: '{field}'")

    if not data["items"]:
        raise ValueError("Invoice must have at least one line item.")

    for i, item in enumerate(data["items"]):
        for field in ["description", "quantity", "unit_price"]:
            if field not in item:
                raise ValueError(f"Item {i + 1} is missing field: '{field}'")


def compute_totals(data: dict) -> dict:
    tax_rate = float(data.get("tax_rate", 0))
    currency_symbol = data.get("currency_symbol", "£")

    items = []
    subtotal = 0.0
    for item in data["items"]:
        qty = float(item["quantity"])
        unit_price = float(item["unit_price"])
        amount = qty * unit_price
        subtotal += amount
        items.append({**item, "amount": amount})

    tax_amount = subtotal * (tax_rate / 100)
    total = subtotal + tax_amount

    return {
        **data,
        "items": items,
        "subtotal": subtotal,
        "tax_rate": tax_rate,
        "tax_amount": tax_amount,
        "total": total,
        "currency_symbol": currency_symbol,
    }


def render_html(data: dict) -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("invoice.html")

    logo_uri = LOGO_PATH.as_uri() if LOGO_PATH.exists() else ""

    return template.render(**data, logo_path=logo_uri)


def generate_pdf(html: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html, base_url=str(BASE_DIR)).write_pdf(str(output_path))


def default_output_name(data: dict) -> Path:
    inv_number = data.get("invoice_number", "invoice").replace("/", "-").replace(" ", "_")
    return OUTPUT_DIR / f"{inv_number}.pdf"


def main():
    parser = argparse.ArgumentParser(description="Generate a professional PDF invoice.")
    parser.add_argument(
        "json_file",
        nargs="?",
        default=str(BASE_DIR / "data" / "sample_invoice.json"),
        help="Path to invoice JSON file (default: data/sample_invoice.json)",
    )
    parser.add_argument(
        "-o", "--output",
        help="Output PDF path (default: output/<invoice_number>.pdf)",
    )
    args = parser.parse_args()

    json_path = Path(args.json_file)
    if not json_path.exists():
        print(f"Error: JSON file not found: {json_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading invoice data from: {json_path}")
    data = load_invoice(json_path)
    data.setdefault("seller", load_seller_from_env())

    print("Validating fields...")
    validate(data)

    print("Computing totals...")
    data = compute_totals(data)

    output_path = Path(args.output) if args.output else default_output_name(data)

    print("Rendering HTML template...")
    html = render_html(data)

    print(f"Generating PDF → {output_path}")
    generate_pdf(html, output_path)

    print(f"\nDone! Invoice saved to: {output_path}")


if __name__ == "__main__":
    main()
