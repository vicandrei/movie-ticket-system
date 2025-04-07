from flask import Flask, render_template, request, send_file
from io import BytesIO
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        
        # Generate the PDF ticket
        pdf_buffer = create_ticket_pdf(name)

        # Serve the PDF file for download
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, download_name=f'{name}_ticket.pdf', as_attachment=True)

    return render_template('index.html')

def create_ticket_pdf(name):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Ticket content
    p.setFont("Helvetica-Bold", 20)
    p.drawString(100, 750, "MOVIE NIGHT TICKET")
    p.setFont("Helvetica", 14)
    p.drawString(100, 700, f"Name: {name}")
    p.drawString(100, 680, "Movie: A Quiet Place")
    p.drawString(100, 660, "Date: Friday, April 25")
    p.drawString(100, 640, "Time: 7:00 PM")
    p.drawString(100, 620, "Venue: Community Center")
    p.drawString(100, 600, "Please show this ticket at the entrance.")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use the port provided by Render, fallback to 5000
    app.run(host='0.0.0.0', port=port, debug=True)
