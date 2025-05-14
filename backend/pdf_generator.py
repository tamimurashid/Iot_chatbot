from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import io
from flask import send_file

def generate_device_pdf_stream(device_id, auth_token):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2.0, height - 50, "Device Authentication Information")

    c.setFont("Helvetica", 12)
    c.drawString(100, height - 100, f"Device ID: {device_id}")
    c.drawString(100, height - 130, f"Auth Token: {auth_token}")
    c.drawString(100, height - 160, f"Issued Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(100, height - 200, "Use this information carefully. Do not share your Auth Token publicly.")

    c.save()
    buffer.seek(0)  # Go to the beginning of the buffer

    # Return as downloadable file directly to the client
    return send_file(buffer, as_attachment=True, download_name="device_info.pdf", mimetype='application/pdf')
