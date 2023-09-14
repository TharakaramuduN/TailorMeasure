import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class MessageSender:
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587  # Port for TLS encryption
    sender_email = 'example@gmail.com'
    sender_password = open(r'C:\Users\DELL\Desktop\SMTP Password.txt',"r").readline()
    # Create the email message
    recipient_email = None
    def create_message(self,username,recipient_email):
        MessageSender.recipient_email = recipient_email
        subject = 'Registration Successful'
        message_body = f"""Thanks for joining with us!
                           Your username is {username} and your default password is 'NewUser'\n
                           To change your password, Please sign in to 'www.rajeswaritailors.com'"""
        message = MIMEMultipart()
        message['From'] = MessageSender.sender_email
        message['To'] = MessageSender.recipient_email
        message['Subject'] = subject
        message.attach(MIMEText(message_body, 'plain'))

        # Establish a connection to the SMTP server
        try:
            smtp_server = smtplib.SMTP(MessageSender.smtp_server, MessageSender.smtp_port)
            smtp_server.starttls()  # Use TLS encryption
            smtp_server.login(MessageSender.sender_email, MessageSender.sender_password)

            # Send the email
            smtp_server.sendmail(MessageSender.sender_email, MessageSender.recipient_email, message.as_string())
            print('Email sent successfully!')

        except smtplib.SMTPException as e:
            print('An error occurred while sending the email:', e)

        finally:
            smtp_server.quit() # Close the SMTP connection
