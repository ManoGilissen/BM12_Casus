import smtplib

from email.mime.text import MIMEText
from subprocess import Popen, PIPE
from time import *

senderMail = "dspnzr2000@gmail.com"
recipientMail = "svenheinen93@gmail.com"
patientName = "Anne Beertens"

testTime = strftime("%A, %d %b %Y om %H:%M:%S", gmtime())

mailPlaintext = patientName + " heeft niet op het medicatie alarm van " + testTime + " gereageerd."
mailMsg= MIMEText(mailPlaintext)
mailMsg['From'] = senderMail
mailMsg['To'] = recipientMail
mailMsg['Subject'] = patientName + " reageert niet op medicatie alarm"

mailProcess = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
mailProcess.communicate(mailMsg.as_string())
