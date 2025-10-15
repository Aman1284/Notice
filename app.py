

import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime
import io

# -----------------------------------------------------
# Streamlit UI
# -----------------------------------------------------
st.set_page_config(page_title="Letter PDF Generator", page_icon="📄")
st.title("📄 Official Letter PDF Generator")

st.write("Generate official school letters with consistent layout and proper signature alignment.")

# Letterhead selector
letterhead_option = st.radio("Choose Letterhead:", ["Just Kids", "JK Public"], horizontal=True)

# Inputs
salutation = st.text_input("Salutation", "Dear Parents,")
message = st.text_area(
    "Enter message body",
    height=200,
    value=(
        "The school will remain closed on the occasion of Deepawali, Chhath, and Bhai Duj "
        "from 20th Oct (Mon) to 28th Oct (Tue).\nRegular classes will resume from 29th Oct."
    ),
)
sender_name = st.text_input("Sender Name", "Dimple Agarwal")
designation = st.text_input("Designation", "Principal")
date = datetime.now().strftime("%d %B %Y")

# -----------------------------------------------------
# PDF Generator
# -----------------------------------------------------
def create_pdf(letterhead_option, salutation, message, sender_name, designation, date):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Select letterhead
    if letterhead_option == "Just Kids":
        letterhead_path = "justkids.png"
    else:
        letterhead_path = "jkpublic.png"

    # Draw letterhead
    try:
        letterhead = ImageReader(letterhead_path)
        c.drawImage(letterhead, 0, 0, width=width, height=height, preserveAspectRatio=True, mask="auto")
    except Exception as e:
        st.warning(f"Letterhead missing: {e}")

    # Layout constants
    left_margin = 80
    right_margin = width - 80
    text_width = right_margin - left_margin
    top_y = height - 230

    # ------------------- Salutation + Date -------------------
    c.setFont("Times-Bold", 14)
    c.drawString(left_margin, top_y, salutation)

    # Smaller, lighter date
    c.setFont("Times-Italic", 14)
    c.drawRightString(right_margin, top_y, f"Date: {date}")

    # ------------------- Message Body -------------------
    message = message.strip()
    if not message.lower().endswith("thanks"):
        message += "\n\nThanks"

    # Preserve line breaks
    message_html = message.replace("\n", "<br/>")

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "BodyText",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=13,
        leading=16,
        textColor=colors.black,
        alignment=0,
    )

    paragraph = Paragraph(message_html, style=body_style)
    para_width, para_height = paragraph.wrap(text_width, 1000)

    # Draw message
    y_text_start = top_y - 40
    y_text_bottom = y_text_start - para_height
    paragraph.drawOn(c, left_margin, y_text_bottom)

    # ------------------- Signature Block -------------------
    # Fixed bottom area for consistent layout
    name_y = 190  # base line for name text

    try:
        signature = ImageReader("Dimple Agarwal.png")
        # Draw signature slightly above the name (10 pts gap)
        sig_height = 50  # signature image height in pts
        sig_bottom_y = name_y + 10  # bottom of signature just above name
        c.drawImage(signature, right_margin - 140, sig_bottom_y, width=200, height=sig_height, mask="auto")
    except Exception as e:
        st.warning(f"Signature missing: {e}")

    # Name & designation below signature
    c.setFont("Times-Bold", 12)
    c.drawRightString(right_margin, name_y, sender_name)
    c.setFont("Times-Roman", 11)
    c.drawRightString(right_margin, name_y - 15, designation)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# -----------------------------------------------------
# Streamlit Action
# -----------------------------------------------------
if st.button("Generate PDF"):
    if not message.strip():
        st.warning("Please enter a message first.")
    else:
        pdf_buffer = create_pdf(letterhead_option, salutation, message, sender_name, designation, date)
        st.download_button(
            label="📥 Download PDF",
            data=pdf_buffer,
            file_name=f"{letterhead_option.replace(' ', '_')}_Notice_{date}.pdf",
            mime="application/pdf",
        )
