import smtplib

import os
from music21 import *

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

import gui.errorGUI as error
import socket

import win32com.client

""" This module contains the controller used to send an email within the midi file at a specified adress. """

class Email:
    """ Controller class, sends an email using a specified adress to the same address.
    """
    @staticmethod
    def write_email(email_recipient, email_password, score, email_subject="Perfect Melody MIDI file"):
        """ Creates the email containing the midi file to send.
            The user sends an email to himself.
            params: 
                email_recipient (str) -> adress used to send and recieve the email
                email_password (str) -> password of email account
                email_subject (str) -> subject of the sent email
                score (music21.stream.Score) -> the score to export at midi format
        """
        msg = MIMEMultipart()

        # text to attach to the mail
        body="You will find the midi file you requested as attachment to this e-mail."
        msg.attach(MIMEText(body, 'plain'))

        # creation of the midi file to send
        fileName = "midi.mid"
        score.write("midi", fileName)
        fileMidi = open(fileName, "rb")

        # creation of the attachment
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload((fileMidi).read())
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', "attachment; filename= %s" %fileName)

        msg.attach(attachment)

        text = msg.as_string()

        # find the server in the string write by the user
        addrToSend = ""
        try:
        	addrToSend = Email.extract_server(email_recipient)
        except Exception:
        	error.ErrorGUI.displayError("Email Error", "No e-mail address")
        	return

        # connexion to the server STMP
        try:
            serverAddr = ""
            port = 587

            # if the server is gmail
            if(addrToSend == 'gmail'):
                serverAddr = 'smtp.gmail.com'
            # if the server is hotmail
            elif(addrToSend == 'hotmail'):
                serverAddr = "smtp.live.com"
            # if the server is outlook
            elif(addrToSend == 'outlook'):
                serverAddr = "smtp-mail.outlook.com"

            # error
            if(addrToSend == ""):
                error.ErrorGUI.displayError("Email Error", "Please note that only gmail, \nhotmail or outlook addresses\ncan send an email")
            # connect to the server
            else:
                server = smtplib.SMTP(serverAddr, port)
                server.starttls()
                server.login(email_recipient, email_password)
                server.sendmail(email_recipient, email_recipient, text)
                server.quit()

        # when an error occured
        except smtplib.SMTPAuthenticationError:
            error.ErrorGUI.displayError("Email Error", "Authentication went wrong")

        except smtplib.SMTPConnectError:
            error.ErrorGUI.displayError("Email Error", "Error occurred during establishment of\na connection with the server.")

        except smtplib.SMTPDataError:
            error.ErrorGUI.displayError("Email Error", "The SMTP server refused to accept \nthe message data.")

        except smtplib.SMTPServerDisconnected:
            error.ErrorGUI.displayError("Email Error", "the server unexpectedly disconnects.")

        except smtplib.SMTPResponseException:
            error.ErrorGUI.displayError("Email Error", "the SMTP server returns an error code.")

        except smtplib.SMTPRecipientsRefused:
            error.ErrorGUI.displayError("Email Error", "recipient address refused.")

        except smtplib.SMTPHeloError :
            error.ErrorGUI.displayError("Email Error", "The server refused smtp's HELO message.")

        except socket.gaierror :
            error.ErrorGUI.displayError("Internet Error", "It seems you have no internet connection.")            

        fileMidi.close()

    @staticmethod
    def extract_server(email_recipient):
        """ Return the server part contained in the email_recipient.
            params: 
                email_recipient (str) -> sender's adress
            return:
                if the function recognizes a server in the adress, it returns the string containing the server
                else, it returns an empty string
        """
        i=0
        stringToReturn = ""
        letter = email_recipient[i]

        # allows to consider only the substring after '@'
        while((letter != '@') & (i != len(email_recipient))):
            i+=1
             # condition if letter is the last letter of the string
            if(i < len(email_recipient)):
                letter = email_recipient[i]

        # skip the '@'
        i+=1

        
        if(i < len(email_recipient)):
            letter = email_recipient[i]

            # stopped when the current letter = '.'
            while((letter != '.') & (i != len(email_recipient))):
                stringToReturn += letter
                i+=1
                # condition if letter is the last letter of the string
                if(i < len(email_recipient)):
                    letter = email_recipient[i]                

            # error
            if (i == len(letter)):
                stringToReturn = ""

        return stringToReturn

