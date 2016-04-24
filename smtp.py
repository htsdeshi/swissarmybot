#!/usr/bin/env python
# encoding: utf-8


import sys
import smtplib
import config

from email.mime.multipart import MIMEMultipart

COMMASPACE = ', '


def main():
    sender = config.mail['username']
    gmail_password = config.mail['password']
    recipients = config.mail['sendto']

    # Create the enclosing (outer) message
    outer = MIMEMultipart()
    outer['Subject'] = 'Page for Deshi'
    outer['To'] = COMMASPACE.join(recipients)
    outer['From'] = sender
    outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'

    composed = outer.as_string()

    # Send the email
    try:
        with smtplib.SMTP(config.mail['server'], 587) as s:
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(sender, gmail_password)
            s.sendmail(sender, recipients, composed)
            s.close()
        print("Email sent!")
    except:
        print("Unable to send the email. Error: ", sys.exc_info()[0])
        raise

if __name__ == '__main__':
    main()
