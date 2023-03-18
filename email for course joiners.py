import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# SMTP server details
smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_username = 'deivadk061@gmail.com'
smtp_password = 'pass0897645312'

# Email details
sender_email = 'deiva@example.com'
recipient_email = 'paul@example.com'
subject = 'Welcome to our course!'
body = '''Dear User,

I would like to extend a warm welcome to you for joining our course [Course Name]. We are thrilled to have you as a part of our community and we believe that this course will prove to be an enriching experience for you.

To ensure that you have a smooth and hassle-free learning experience, we have created a Telegram group exclusively for our course participants. You can use this group to connect with your peers, ask questions, and get real-time support from our instructors.

Please click on the following link to join the group: [Insert Telegram group link]

In addition, I would like to remind you that the course material and other important announcements will be shared through our learning management system (LMS). You should have received an email with login credentials for the LMS. If you have not received it yet, please let us know and we will send it to you at the earliest.

Once again, welcome to the course! We look forward to seeing you in the Telegram group and on our LMS.

Best regards,
MON_SCHOOL TEAM'''

# Create a multipart message to hold the email content
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = recipient_email
msg['Subject'] = subject

# Add body to email
msg.attach(MIMEText(body, 'plain'))

# Start the SMTP server and send the email
with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(sender_email, recipient_email, msg.as_string())

print('Email sent successfully!')

