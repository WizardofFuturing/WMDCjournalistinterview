from flask import Flask, request, jsonify
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

def send_email(conversation_text):
    sender_email = "interview@wmdc.media"
    receiver_email = "worldoffuturing@gmail.com"
    username = "interview@wmdc.media"
    password = "LvG[z6WKn!S;"
    smtp_server = "wmdc.media"
    smtp_port = 465

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
    
    send_email(conversation_text)
    return jsonify({"status": "Email sent successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)


