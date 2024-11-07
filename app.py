from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

# Configure logging
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

# In-memory storage for session activity timestamps
session_activity = {}

def send_email(conversation_text):
    message = MIMEMultipart("alternative")
    message["Subject"] = "New GPT Conversation Summary"
    message["From"] = sender_email
    message["To"] = receiver_email
    part = MIMEText(conversation_text, "plain")
    message.attach(part)

    try:
        logger.info(f"Attempting to send email at {datetime.now()}")
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(username, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            logger.info("Email sent successfully")
            return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication Error: {e}")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP Error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")
        return False

@app.route('/send-email', methods=['POST'])
def send_email_endpoint():
    try:
        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({"error": "No JSON data received"}), 400
        
        conversation_text = data.get('conversation_text')
        if not conversation_text:
            logger.error("Missing conversation_text")
            return jsonify({"error": "Missing conversation_text"}), 400
        
        # Update the activity timestamp and store conversation
        current_time = datetime.now()
        session_activity['last_activity'] = current_time
        session_activity['conversation_text'] = conversation_text
        
        # Attempt immediate send if no recent activity
        last_send = session_activity.get('last_send')
        if not last_send or (current_time - last_send > timedelta(minutes=10)):
            success = send_email(conversation_text)
            if success:
                session_activity['last_send'] = current_time
                session_activity.clear()  # Clear after successful send
                return jsonify({"status": "Email sent successfully"}), 200
            else:
                return jsonify({"error": "Failed to send email"}), 500
        
        logger.info(f"Email queued for inactivity check. Current session activity: {session_activity}")
        return jsonify({"status": "Email queued for inactivity check"}), 200
        
    except Exception as e:
        logger.error(f"Error in send_email_endpoint: {e}")
        return jsonify({"error": str(e)}), 500

def check_for_inactive_sessions():
    try:
        logger.info(f"Checking for inactive sessions at {datetime.now()}")
        logger.info(f"Current session activity: {session_activity}")
        
        last_activity = session_activity.get('last_activity')
        if last_activity and datetime.now() - last_activity > timedelta(minutes=10):
            conversation_text = session_activity.get('conversation_text', 'No conversation text available.')
            logger.info("Inactive session found, attempting to send email")
            if send_email(conversation_text):
                session_activity.clear()  # Clear only after successful send
                logger.info("Inactive session email sent and session cleared")
            else:
                logger.error("Failed to send email for inactive session")
    except Exception as e:
        logger.error(f"Error in check_for_inactive_sessions: {e}")

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(check_for_inactive_sessions, 'interval', minutes=1)  # Check more frequently
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
