from flask import Flask, render_template, request, send_file
import qrcode
from io import BytesIO
from flask_mail import Mail, Message
import os
import base64
from dotenv import load_dotenv

# Load .env file
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path, override=True)

# Debug print
print("MAIL_PORT =", os.getenv("MAIL_PORT"))  # Should print 587 or a value

# Initialize Flask app
app = Flask(__name__)

# Mail configuration
try:
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
except Exception as e:
    print("❌ Error loading mail configuration:", e)

mail = Mail(app)

# Home route - QR generator
@app.route('/', methods=['GET', 'POST'])
def index():
    qr_image_data = None

    if request.method == 'POST':
        data = request.form.get('data')
        if data:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_b64 = base64.b64encode(buffered.getvalue()).decode()
            qr_image_data = f"data:image/png;base64,{img_b64}"

    return render_template('index.html', qr_image_data=qr_image_data)

# Contact form route
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        if request.form.get('middle_name'):  # honeypot
            return "Nice try, bot 🤖", 403

        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        msg = Message(
            subject=f"QRContact from {name}",
            sender=email,
            recipients=[app.config['MAIL_USERNAME']],
            body=message
        )
        mail.send(msg)
        return render_template('contact.html', success=True)

    return render_template('contact.html')

# Run app
if __name__ == '__main__':
    app.run(debug=True)
