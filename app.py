import os
from io import BytesIO
from flask import Flask, render_template, request, send_file
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

app = Flask(__name__)

def create_ticket_pdf(name):
    # — Setup PDF canvas in landscape
    buffer = BytesIO()
    page_w, page_h = landscape(letter)
    p = canvas.Canvas(buffer, pagesize=(page_w, page_h))

    # Margins and ticket dimensions
    margin = 30
    ticket_x = margin
    ticket_y = margin
    ticket_w = page_w - 2*margin
    ticket_h = page_h - 2*margin

    # — Draw page background
    p.setFillColor(colors.HexColor("#f0f4f8"))
    p.rect(0, 0, page_w, page_h, fill=True, stroke=False)

    # — Draw ticket body & border
    p.setFillColor(colors.white)
    p.roundRect(ticket_x, ticket_y, ticket_w, ticket_h, radius=20, fill=True, stroke=False)
    p.setStrokeColor(colors.HexColor("#2c3e50"))
    p.setLineWidth(3)
    p.roundRect(ticket_x, ticket_y, ticket_w, ticket_h, radius=20, fill=False, stroke=True)


    # — Prepare text block (title + details)
    lines = [
        ("Helvetica-Bold", 24, "RCCG DPP"),
        ("Helvetica-Bold", 18, "YOUTH MOVIE NIGHT TICKET"),
        ("Helvetica", 14, f"Name: {name}"),
        ("Helvetica", 14, "Date: Saturday, April 19th"),
        ("Helvetica", 14, "Time: 5:00 PM"),
        ("Helvetica", 14, "Venue: Church Auditorium, 14 Oyedara St, Ojokoro Newtown, Agric, Ikorodu, Lagos"),
    ]
    # Calculate total block height
    spacing = 8
    block_height = sum(font_size + spacing for _, font_size, _ in lines) - spacing

    # Starting Y so block is vertically centered
    start_y = ticket_y + (ticket_h + block_height)/2

    center_x = ticket_x + ticket_w/2
    y = start_y
    for font_name, font_size, text in lines:
        p.setFont(font_name, font_size)
        p.setFillColor(colors.HexColor("#2c3e50") if font_name.endswith("Bold") else colors.black)
        p.drawCentredString(center_x, y, text)
        y -= font_size + spacing

    # — Draw QR code under text block, centered
    qr_data = "rccg dpp movie night 2025"
    qr_size = 80
    qr = QrCodeWidget(qr_data)
    bounds = qr.getBounds()
    qr_width = bounds[2] - bounds[0]
    qr_height = bounds[3] - bounds[1]
    # Scale to qr_size
    d = Drawing(qr_size, qr_size, transform=[qr_size/qr_width,0,0,qr_size/qr_height,0,0])
    d.add(qr)
    qr_x = center_x - qr_size/2
    qr_y = ticket_y + margin
    renderPDF.draw(d, p, qr_x, qr_y)

    # — Stickers in top corners
    sticker_size = 60
    try:
        p.drawImage("static/images/popcorn.png",
                    ticket_x + 10, ticket_y + ticket_h - sticker_size - 10,
                    sticker_size, sticker_size, mask='auto')
        p.drawImage("static/images/film.png",
                    ticket_x + ticket_w - sticker_size - 10, ticket_y + ticket_h - sticker_size - 10,
                    sticker_size, sticker_size, mask='auto')
    except IOError:
        pass

    # — Footer note below QR code
    p.setFont("Helvetica-Oblique", 10)
    p.setFillColor(colors.grey)
    p.drawCentredString(center_x, qr_y - 15, "Please show this ticket at the entrance. Thank you!")

    # — Finish up
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name', 'Guest').strip() or 'Guest'
        pdf = create_ticket_pdf(name)
        return send_file(
            pdf,
            as_attachment=True,
            download_name=f"{name.replace(' ', '_')}_ticket.pdf",
            mimetype='application/pdf'
        )
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)