import smtplib
import ssl

smtp_server = "smtp.hostinger.com"
port = 587  # For starttls
sender_email = "help@qrproject.tech"
password = "Helpqr@48"
receiver_email = "akhisou1827@gmail.com"
message = """From:UMHB Admin <help@qrproject.tech>
To: me
MIME-Version: 1.0
Content-type: text/html
Subject: Account Created in UMHB

An account has been created by UMHB Admin for you.<br><br>Your student id is 13, and your password is 'sai'.<br><br>Userid and Password are confidential.<br><br>Regards,<br><br>UMHB Admin,<br><br>help@qrproject.tech
"""
# Create a secure SSL context
context = ssl.create_default_context()

# Try to log in to server and send email
try:
    server = smtplib.SMTP(smtp_server, port)
    server.ehlo()  # Can be omitted
    server.starttls(context=context)  # Secure the connection
    server.ehlo()  # Can be omitted
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
except Exception as e:
    # Print any error messages to stdout
    print(e)
finally:
    server.quit()
