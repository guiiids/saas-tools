from flask import Flask, request, jsonify, render_template
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.get_json()
    message = Mail(
        from_email='gui.vieiraa@gmail.com',  # Replace with your verified sender email
        to_emails=data['email'],
        subject=data['subject'],
        html_content=data['message'])
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        return jsonify({'message': 'Email sent successfully!', 'status_code': response.status_code}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'status_code': response.status_code if 'response' in locals() else 'N/A'}), 500

if __name__ == '__main__':
    app.run(debug=True)