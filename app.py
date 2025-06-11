from flask import Flask, render_template, request, send_file
import qrcode
from io import BytesIO
from livereload import Server
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
import base64

# Initialize app and config
app = Flask(__name__)
load_dotenv()

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

# Initialize mail AFTER config
mail = Mail(app)

# Routes
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


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        if request.form.get('middle_name'):
            return "Nice try, bot 🤖", 403

        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        msg = Message(subject=f"QRContact from {name}",
                      sender=email,
                      recipients=[app.config['MAIL_USERNAME']],
                      body=message)

        mail.send(msg)
        return render_template('contact.html', success=True)

    return render_template('contact.html')


# LiveReload + server start
if __name__ == '__main__':
    server = Server(app.wsgi_app)
    server.watch('static/')
    server.watch('templates/')
    server.serve(open_url_delay=False)
