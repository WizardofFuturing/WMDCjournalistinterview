from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

# Email configuration
sender_email = "interview@wmdc.media"
receiver_email = "worldoffuturing@gmail.com"
username = "interview@wmdc.media"
password = "LvG[z6WKn!S;"
smtp_server = "wmdc.media"
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
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(username, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route('/send-email', methods=['POST'])
def send_email_endpoint():
    data = request.get_json()
    conversation_text = data.get('conversation_text')
    if not conversation_text:
        return jsonify({"error": "Missing conversation_text"}), 400
    
    session_activity['last_activity'] = datetime.now()  # Update the activity timestamp
    session_activity['conversation_text'] = conversation_text  # Store the latest conversation
    return jsonify({"status": "Email queued for inactivity check"}), 200

def check_for_inactive_sessions():
    last_activity = session_activity.get('last_activity')
    if last_activity and datetime.now() - last_activity > timedelta(minutes=10):
        conversation_text = session_activity.get('conversation_text', 'No conversation text available.')
        send_email(conversation_text)
        session_activity.clear()  # Clear the session after sending the email

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(check_for_inactive_sessions, 'interval', minutes=5)  # Run check every 5 minutes
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
