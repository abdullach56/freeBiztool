from __future__ import annotations

import io
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from flask import Flask, jsonify, redirect, render_template, request, send_file, url_for
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle

app = Flask(__name__)

# global configuration values
# your AdSense publisher ID; used in templates to initialise the script tag
ADSENSE_CLIENT = "ca-pub-4803874079186263"


@app.context_processor
def inject_globals() -> Dict[str, Any]:
    # values available in all templates
    return {"adsense_client": ADSENSE_CLIENT}


def as_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def safe_decimal(raw: str | int | float | None, default: Decimal = Decimal("0")) -> Decimal:
    try:
        if raw is None or raw == "":
            return default
        return Decimal(str(raw))
    except (InvalidOperation, ValueError):
        return default


@app.route("/")
def home():
    return redirect(url_for("gst_calculator"))


@app.route("/gst-calculator")
def gst_calculator():
    title = "GST Calculator"
    desc = "Calculate GST instantly with CGST and SGST split."
    canonical = request.base_url
    structured = {
        "@context": "http://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": desc,
        "url": canonical,
    }
    return render_template(
        "gst_calculator.html",
        page_title=title,
        page_description=desc,
        canonical_url=canonical,
        structured_data=structured,
    )


@app.route("/reverse-gst-calculator")
def reverse_gst_calculator():
    title = "Reverse GST Calculator"
    desc = "Find the pre-GST amount or GST component from a total value quickly."
    canonical = request.base_url
    structured = {
        "@context": "http://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": desc,
        "url": canonical,
    }
    return render_template(
        "reverse_gst_calculator.html",
        page_title=title,
        page_description=desc,
        canonical_url=canonical,
        structured_data=structured,
    )


@app.route("/discount-calculator")
def discount_calculator():
    title = "Discount Calculator"
    desc = "Quickly compute sale prices, markups and savings with our discount tool."
    canonical = request.base_url
    structured = {
        "@context": "http://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": desc,
        "url": canonical,
    }
    return render_template(
        "discount_calculator.html",
        page_title=title,
        page_description=desc,
        canonical_url=canonical,
        structured_data=structured,
    )


@app.route("/invoice-generator")
def invoice_generator():
    title = "Invoice Generator"
    desc = "Generate professional GST-compliant invoices and download them as PDF."
    canonical = request.base_url
    structured = {
        "@context": "http://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": desc,
        "url": canonical,
    }
    return render_template(
        "invoice_generator.html",
        page_title=title,
        page_description=desc,
        canonical_url=canonical,
        structured_data=structured,
    )


@app.post("/api/invoice-pdf")
def invoice_pdf():
    payload = request.get_json(silent=True) or {}
    seller = payload.get("seller", {})
    customer = payload.get("customer", {})
    items = payload.get("items", [])

    parsed_items = []
    subtotal = Decimal("0")
    total_gst = Decimal("0")

    for item in items:
        quantity = safe_decimal(item.get("quantity"), Decimal("0"))
        price = safe_decimal(item.get("price"), Decimal("0"))
        gst_rate = safe_decimal(item.get("gstRate"), Decimal("0"))

        line_subtotal = quantity * price
        line_gst = line_subtotal * gst_rate / Decimal("100")
        line_total = line_subtotal + line_gst

        subtotal += line_subtotal
        total_gst += line_gst

        parsed_items.append(
            {
                "name": str(item.get("name", "")).strip() or "Item",
                "quantity": as_money(quantity),
                "price": as_money(price),
                "gst_rate": as_money(gst_rate),
                "line_total": as_money(line_total),
            }
        )

    grand_total = subtotal + total_gst

    # build the PDF using Platypus for cleaner tables and automatic paging
    buffer = io.BytesIO()

    # document template with margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    story: list[Any] = []

    # title & generated timestamp
    story.append(Paragraph("<b>Tax Invoice</b>", styles["Title"]))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # seller/customer details as a two‑column table
    seller_lines = [
        seller.get("businessName", ""),
        seller.get("address", ""),
        f"GST: {seller.get('gstNumber', '')}",
        f"Phone: {seller.get('phone', '')}",
    ]
    customer_lines = [
        customer.get("name", ""),
        customer.get("address", ""),
        f"GST: {customer.get('gstNumber', '')}" if customer.get("gstNumber") else "GST: -",
    ]

    # pad the shorter list so table rows line up
    max_len = max(len(seller_lines), len(customer_lines))
    seller_lines += [""] * (max_len - len(seller_lines))
    customer_lines += [""] * (max_len - len(customer_lines))

    contact_data = [
        [Paragraph("<b>Seller</b>", styles["Normal"]), Paragraph("<b>Customer</b>", styles["Normal"])]
    ]
    for s, c in zip(seller_lines, customer_lines):
        contact_data.append([s, c])

    contact_table = Table(contact_data, colWidths=[doc.width / 2.0] * 2)
    contact_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    story.append(contact_table)
    story.append(Spacer(1, 20))

    # items table
    headers = ["Item", "Qty", "Price", "GST%", "Total"]
    data = [headers]
    for row in parsed_items:
        data.append(
            [
                row["name"],
                f"{row['quantity']}",
                f"{row['price']}",
                f"{row['gst_rate']}",
                f"{row['line_total']}",
            ]
        )

    col_widths = [doc.width * 0.4, doc.width * 0.1, doc.width * 0.15, doc.width * 0.15, doc.width * 0.2]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table_style = TableStyle(
        [
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]
    )
    table.setStyle(table_style)
    story.append(table)
    story.append(Spacer(1, 12))

    # totals
    totals_data = [
        ["Subtotal", f"INR {as_money(subtotal)}"],
        ["Total GST", f"INR {as_money(total_gst)}"],
        ["<b>Grand Total</b>", f"<b>INR {as_money(grand_total)}</b>"],
    ]
    totals_table = Table(totals_data, colWidths=[doc.width * 0.6, doc.width * 0.4])
    totals_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(totals_table)

    # build document
    doc.build(story)

    buffer.seek(0)
    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="invoice.pdf",
    )


if __name__ == "__main__":
    app.run(debug=True)
