from flask import Flask, request, jsonify
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Email configuration
sender_email = "interview@wmdc.media"
receiver_email = "worldoffuturing@gmail.com"
username = "interview@wmdc.media"
password = "LvG[z6WKn!S;"
smtp_server = "premium280.web-hosting.com"
smtp_port = 465

def send_email(conversation_text, participant_email=None):
    message = MIMEMultipart("alternative")
    message["Subject"] = "New GPT Interview Summary"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Add participant email to the summary if provided
    if participant_email:
        email_content = f"Participant Email: {participant_email}\n\nInterview Summary:\n{conversation_text}"
    else:
        email_content = f"Interview Summary:\n{conversation_text}"

    part = MIMEText(email_content, "plain")
    message.attach(part)

    try:
        logger.info(f"Sending interview summary email at {datetime.now()}")
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(username, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            logger.info("Interview summary email sent successfully")
            return True
    except Exception as e:
        logger.error(f"Error sending interview summary email: {e}")
        return False

@app.route('/send-email', methods=['POST'])
def send_email_endpoint():
    try:
        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({"error": "No JSON data received"}), 400
        
        conversation_text = data.get('conversation_text')
        participant_email = data.get('participant_email')  # Optional
        is_interview_complete = data.get('interview_complete', False)  # New flag
        
        if not conversation_text:
            logger.error("Missing conversation_text")
            return jsonify({"error": "Missing conversation_text"}), 400

        # Send email if either:
        # 1. Interview is marked as complete
        # 2. Participant email is provided
        if is_interview_complete or participant_email:
            success = send_email(conversation_text, participant_email)
            if success:
                return jsonify({"status": "Interview summary email sent successfully"}), 200
            else:
                return jsonify({"error": "Failed to send interview summary email"}), 500
        else:
            return jsonify({"status": "No trigger condition met for sending email"}), 200

    except Exception as e:
        logger.error(f"Error in send_email_endpoint: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
