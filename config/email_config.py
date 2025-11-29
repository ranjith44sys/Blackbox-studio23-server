
import os
from flask_mail import Mail, Message

mail = Mail()

def init_mail(app):
    """Initialize Flask-Mail with app config"""
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    
    # Debug: Print config to verify (remove in production)
    print("Mail Configuration:")
    print(f"MAIL_SERVER: {app.config['MAIL_SERVER']}")
    print(f"MAIL_PORT: {app.config['MAIL_PORT']}")
    print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
    print(f"MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")
    
    mail.init_app(app)
    return mail

def send_contact_notification(contact_data):
    """Send email notification when contact form is submitted"""
    try:
        # Get recipient and sender from environment
        recipient = os.getenv('RECIPIENT_EMAIL', 'lindsay@lindsayadler.com')
        sender = os.getenv('MAIL_DEFAULT_SENDER')
        
        # Validate sender exists
        if not sender:
            print("ERROR: MAIL_DEFAULT_SENDER not configured in .env file")
            return False
        
        print(f"Sending email from {sender} to {recipient}")
        
        msg = Message(
            subject=f"New Contact Form Submission from {contact_data['firstName']} {contact_data['lastName']}",
            sender=sender,  # Explicitly set sender
            recipients=[recipient],
            reply_to=contact_data['email'],  # Set reply-to as the contact's email
            body=f"""
New contact form submission received:

Name: {contact_data['firstName']} {contact_data['lastName']}
Email: {contact_data['email']}
Submitted At: {contact_data.get('submittedAt', 'N/A')}

Message:
{contact_data['message']}

---
This is an automated message from Lindsay Adler Photography website.
            """,
            html=f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #ef4444;">New Contact Form Submission</h2>
    
    <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0;">
        <p><strong>Name:</strong> {contact_data['firstName']} {contact_data['lastName']}</p>
        <p><strong>Email:</strong> <a href="mailto:{contact_data['email']}">{contact_data['email']}</a></p>
        <p><strong>Submitted At:</strong> {contact_data.get('submittedAt', 'N/A')}</p>
    </div>
    
    <div style="margin: 20px 0;">
        <h3 style="color: #333;">Message:</h3>
        <p style="background-color: #fff; padding: 15px; border-left: 4px solid #ef4444;">
            {contact_data['message']}
        </p>
    </div>
    
    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
    <p style="color: #999; font-size: 12px;">
        This is an automated message from Lindsay Adler Photography website.
    </p>
</body>
</html>
            """
        )
        
        mail.send(msg)
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
# MONGO_URI = mongodb://localhost:27017

# # Email Configuration
# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
# MAIL_USE_TLS=True
# MAIL_USERNAME=BlackBoxStudio23@gmail.com
# MAIL_PASSWORD=xjpo umhw ieqd qeei
# MAIL_DEFAULT_SENDER=blackboxstudio23@gmail.com
# RECIPIENT_EMAIL=blackboxstudio23@gmail.com
# # ucwo nibv opti ztzs