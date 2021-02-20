import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.encoders import encode_base64

def send_mail_gmail(toaddrs_list,msg_text,subject="Test",username=None,password=None,attachment_path_list=None):

    if (username is None or password is None):
        username = os.environ.get('SERVICE_EMAIL_SENDER')
        password = os.environ.get('SERVICE_EMAIL_SENDER_PASS')

    s = smtplib.SMTP('smtp.gmail.com:587')
    s.starttls()
    s.login(username, password)
    msg = MIMEMultipart()
    recipients = toaddrs_list
    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = ", ".join(recipients)
    if attachment_path_list is not None:
        for each_file_path in attachment_path_list:
            try:
                file_name=each_file_path.split("/")[-1]
                part = MIMEBase('application', "octet-stream")
                part.set_payload(open(each_file_path, "rb").read())
                encode_base64(part)
                part.add_header('Content-Disposition', 'attachment' ,filename=file_name)
                msg.attach(part)
            except:
                print("could not attach file")
    msg.attach(MIMEText(msg_text,'html'))
    s.sendmail(username, recipients, msg.as_string())
