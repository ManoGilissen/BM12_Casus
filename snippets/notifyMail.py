import smtplib

from email.mime.text import MIMEText
from subprocess import Popen, PIPE
from time import *

#defineer adres, naam, timeformat
senderMail = "dspnzr2000@gmail.com"
recipientMail = "svenheinen93@gmail.com"
patientName = "Anne Beertens"

testTime = strftime("%A, %d %b %Y om %H:%M:%S", localtime())

mailPlaintext = patientName + " heeft niet op het medicatie alarm van " + testTime + " gereageerd."
#Mail wordt omgezet naar MIMEtype text voor compabiliteit
mailMsg= MIMEText(mailPlaintext)
mailMsg['From'] = senderMail
mailMsg['To'] = recipientMail
mailMsg['Subject'] = patientName + " reageert niet op medicatie alarm"

#Inhoud van variabele mailMsg wordt gepiped naar sendmail process
mailProcess = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
mailProcess.communicate(mailMsg.as_string())