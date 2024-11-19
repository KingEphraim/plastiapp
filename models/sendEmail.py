import smtplib,json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

with open('config.json') as f:
    config = json.load(f) 

def send_email(subject, body, to_email):
    # Your email credentials
    from_email = config['emailServerFromEmail']
    password = config['emailServerPassword']
    
    # Setup the MIME
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # Attach the body of the email
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server securely using SSL
        server = smtplib.SMTP_SSL('mail.cardknoxdemo.com', 465)  # Use SSL directly for port 465
        server.login(from_email, password)  # Login to the email server

        # Send the email
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        print("Email sent successfully!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.quit()
