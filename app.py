import os
import re
import base64
from flask import Flask, request, jsonify, render_template
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail, Attachment, FileContent, FileName, FileType, Disposition
)
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Requires: pip install html2text
import html2text

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/text-editor')
def txt_editor():
    return render_template('text-editor.html')

@app.route('/another-page')
def another_page():
    return render_template('another-page.html')  # Create another-page.html in the templates directory

@app.route('/send-email', methods=['POST'])
def send_email():
    data = request.get_json()
    html_content = data['message']
    
    # Predefined recipient email address
    recipient_email = os.getenv('RECIPIENT_EMAIL')
    
    # Regex to find base64-encoded images in the HTML
    pattern = r'(<img[^>]+src="data:(image/\w+);base64,([^"]+)"[^>]*>)'
    matches = re.findall(pattern, html_content)

    attachments = []

    # Convert each embedded base64 image to an attachment
    for idx, match in enumerate(matches):
        full_tag = match[0]
        mime_type = match[1]
        b64_data = match[2]
        
        attachment = Attachment()
        attachment.file_content = FileContent(b64_data)
        attachment.file_type = FileType(mime_type)
        attachment.file_name = FileName(f'image_{idx}.png')
        attachment.disposition = Disposition('attachment')
        attachments.append(attachment)

        # Replace the <img> tag in the HTML with a placeholder that shows the filename
        placeholder = f"[Embedded image attached: image_{idx}.png]"
        html_content = html_content.replace(full_tag, placeholder)

    # Convert the (now modified) HTML to Markdown text
    md_content = html2text.html2text(html_content)

    # Create a .doc file attachment
    doc_base64 = base64.b64encode(md_content.encode()).decode()
    doc_attachment = Attachment(
        file_content=FileContent(doc_base64),
        file_type=FileType('application/msword'),
        file_name=FileName('content.doc'),
        disposition=Disposition('attachment')
    )
    attachments.append(doc_attachment)

    # Build the email. The body is now just a placeholder, since the content is in attachments
    message = Mail(
        from_email='gui.vieiraa@gmail.com',  # Replace with your verified sender email
        to_emails='gui.vieiraa2@gmail.com',
        subject=data['subject'],
        html_content='Please see attached Word document and images (if any).'
    )

    # Attach the images (if any) and the .doc file
    for att in attachments:
        message.add_attachment(att)

    try:
        sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        if not sendgrid_api_key:
            app.logger.error("SendGrid API key is missing.")
            return jsonify({'error': 'SendGrid API key is missing.'}), 500

        sg = SendGridAPIClient(sendgrid_api_key)
        
        # Log the message object for debugging
        app.logger.debug(f"SendGrid message: {message.get()}")
        
        response = sg.send(message)
        return jsonify({'message': 'Email sent successfully!', 'status_code': response.status_code}), 200
    except Exception as e:
        app.logger.exception("Error sending email:")
        return jsonify({
            'error': str(e),
            'status_code': response.status_code if 'response' in locals() else 'N/A'
        }), 500

@app.route('/check-api-key')
def check_api_key():
    sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
    if (sendgrid_api_key):
        return jsonify({'message': 'SendGrid API key is set.'}), 200
    else:
        return jsonify({'error': 'SendGrid API key is missing.'}), 500

# Make the scrap function inactive
# @app.route('/scrape-content', methods=['POST'])
# def scrape_content():
#     data = request.get_json()
#     url = data.get('url')
#     if not url:
#         return jsonify({'error': 'URL is missing.'}), 400

#     try:
#         response = requests.get(url)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.content, 'html.parser')
#         content = soup.get_text()  # Adjust this to extract the desired content
#         return jsonify({'content': content}), 200
#     except requests.RequestException as e:
#         return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)