from flask import Flask, request, jsonify
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import traceback
import sys

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Add root route
@app.route('/')
def root():
    return jsonify({
        "status": "running",
        "message": "WMDC GPT Journalist Interview API is running",
        "endpoints": {
            "send-email": "/send-email (POST)"
        },
        "timestamp": datetime.now().isoformat()
    })

# Email configuration
sender_email = "interview@wmdc.media"
receiver_email = "worldoffuturing@gmail.com"
username = "interview@wmdc.media"
password = "LvG[z6WKn!S;"
smtp_server = "premium280.web-hosting.com"
smtp_port = 465

def send_email(conversation_text, participant_email=None):
    message = MIMEMultipart("alternative")
    message["Subject"] = f"New GPT Interview Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Add participant email and timestamp to the summary if provided
    email_content = f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    if participant_email:
        email_content += f"Participant Email: {participant_email}\n"
    email_content += f"\nInterview Summary:\n{conversation_text}"

    part = MIMEText(email_content, "plain")
    message.attach(part)

    try:
        logger.info(f"Attempting to send interview summary email at {datetime.now()}")
        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30) as server:
            # Log connection success
            logger.info("Successfully established SMTP SSL connection")
            
            # Attempt login
            server.login(username, password)
            logger.info("Successfully logged into SMTP server")
            
            # Send email
            server.sendmail(sender_email, receiver_email, message.as_string())
            logger.info("Interview summary email sent successfully")
            return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication Error: {str(e)}")
        logger.error(traceback.format_exc())
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP Error: {str(e)}")
        logger.error(traceback.format_exc())
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email: {str(e)}")
        logger.error(traceback.format_exc())
        return False

@app.route('/send-email', methods=['POST'])
def send_email_endpoint():
    try:
        # Log incoming request
        logger.info(f"Received email request at {datetime.now()}")
        
        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({"error": "No JSON data received"}), 400
        
        # Log request data (excluding sensitive info)
        logger.info(f"Request contains conversation_text: {bool(data.get('conversation_text'))}")
        logger.info(f"Request contains participant_email: {bool(data.get('participant_email'))}")
        logger.info(f"Interview complete flag: {data.get('interview_complete', False)}")
        
        conversation_text = data.get('conversation_text')
        participant_email = data.get('participant_email')
        is_interview_complete = data.get('interview_complete', False)
        
        if not conversation_text:
            logger.error("Missing conversation_text")
            return jsonify({"error": "Missing conversation_text"}), 400

        # Attempt to send email with retry
        for attempt in range(2):  # Try twice
            if attempt > 0:
                logger.info(f"Retry attempt {attempt}")
            
            success = send_email(conversation_text, participant_email)
            if success:
                return jsonify({
                    "status": "Interview summary email sent successfully",
                    "timestamp": datetime.now().isoformat()
                }), 200
            elif attempt < 1:  # If first attempt failed, wait briefly and retry
                logger.info("First attempt failed, waiting to retry...")
                import time
                time.sleep(2)  # Wait 2 seconds before retry
        
        # If we get here, both attempts failed
        return jsonify({
            "error": "Failed to send interview summary email after retries",
            "timestamp": datetime.now().isoformat()
        }), 500

    except Exception as e:
        logger.error(f"Error in send_email_endpoint: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
