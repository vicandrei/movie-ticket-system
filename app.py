from flask import Flask, render_template, request, send_file
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')  # Get name from form
        if name:
            pdf = create_ticket_pdf(name)
            return send_file(pdf, as_attachment=True, download_name="ticket.pdf", mimetype="application/pdf")
    return render_template('index.html')

def create_ticket_pdf(name):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)

    # Page margins
    margin = 30
    width, height = letter

    # Ticket Background
    p.setFillColor(colors.whitesmoke)
    p.rect(margin, margin, width - 2*margin, height - 2*margin, fill=True)

    # Title
    p.setFont("Helvetica-Bold", 24)
    p.setFillColor(colors.darkblue)
    p.drawString(margin + 20, height - margin - 50, "MOVIE NIGHT TICKET")

    # Ticket Info Section
    p.setFont("Helvetica", 14)
    p.setFillColor(colors.black)

    # Add Name
    p.drawString(margin + 20, height - margin - 100, f"Name: {name}")
    
    # Add Movie Details
    p.setFont("Helvetica", 12)
    p.drawString(margin + 20, height - margin - 150, "Date: Saturday, April 19th")
    p.drawString(margin + 20, height - margin - 170, "Time: 5:00 PM")
    p.drawString(margin + 20, height - margin - 190, "Venue: Church Auditorium at 14, Oyedara Street, Ojokoro Newtown, Agric, Ikorodu, Lagos")
    p.drawString(margin + 20, height - margin - 210, "Please show this ticket at the entrance.")

    # Footer section with a reminder message
    p.setFont("Helvetica-Italic", 10)
    p.setFillColor(colors.grey)
    p.drawString(margin + 20, height - margin - 230, "Thank you for reserving your spot!")

    # Add a ticket border
    p.setStrokeColor(colors.blue)
    p.setLineWidth(2)
    p.rect(margin + 10, margin + 10, width - 2*margin - 20, height - 2*margin - 20)

    # Finalize the page and save the PDF
    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use the port provided by Render, fallback to 5000
    app.run(host='0.0.0.0', port=port, debug=True)
