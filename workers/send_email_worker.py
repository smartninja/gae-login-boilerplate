import logging
import sendgrid
from sendgrid.helpers import mail as sendgrid_mail
from google.appengine.api import mail as gae_mail

from handlers.base import BaseHandler
from utils.check_localhost import is_local
from utils.secrets import get_sendgrid_api_key


class SendEmailWorker(BaseHandler):
    def post(self):
        sender_email = self.request.get("sender_email")
        sender_name = self.request.get("sender_name")
        receiver_email = self.request.get("receiver_email")
        email_subject = self.request.get("email_subject")
        content = self.request.get("content")

        if not is_local():
            send_via_provider(provider="google", sender_email=sender_email, sender_name=sender_name,
                              receiver_email=receiver_email, email_subject=email_subject, content=content)
        else:
            # if you're on localhost, the email will show up in your Terminal, but will not be really sent
            logging.info("LOCALHOST: sending email, but not really :)")
            logging.info("Sender: %s" % sender_email)
            logging.info("Receiver: %s" % receiver_email)
            logging.info("Subject: %s" % email_subject)
            logging.info("Message: %s" % content)


def send_via_provider(provider, sender_email, sender_name, receiver_email, email_subject, content):
    """This eases up switching to a new emailing provider."""
    if provider == "google":
        send_via_google(sender_email=sender_email, sender_name=sender_name, receiver_email=receiver_email,
                        email_subject=email_subject, content=content)
    elif provider == "sendgrid":
        send_via_sendgrid(sender_email=sender_email, sender_name=sender_name, receiver_email=receiver_email,
                          email_subject=email_subject, content=content)


def send_via_google(sender_email, sender_name, receiver_email, email_subject, content):
    """Send email via in-built sender on Google App Engine."""
    gae_mail.send_mail(sender="{0}, <{1}>".format(sender_name, sender_email),
                       to=receiver_email,
                       subject=email_subject,
                       body=content)


def send_via_sendgrid(sender_email, sender_name, receiver_email, email_subject, content):
    SENDGRID_API_KEY = get_sendgrid_api_key()  # make sure to create this get_sendgrid_api_key() function in utils/secrets.py first
    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

    email_message = sendgrid_mail.Mail()
    email_message.set_from(sendgrid_mail.Email(sender_email, sender_name))
    email_message.set_subject(email_subject)
    email_message.add_content(sendgrid_mail.Content("text/html", content))

    personalization = sendgrid_mail.Personalization()
    personalization.add_to(sendgrid_mail.Email(receiver_email))

    email_message.add_personalization(personalization)

    try:
        response = sg.client.mail.send.post(request_body=email_message.get())

        if str(response.status_code)[:1] != "2":  # success codes start with 2, for example 200, 201, 202, ...
            logging.error("status code: " + str(response.status_code))
            logging.error("headers: " + str(response.headers))
            return logging.error("body: " + str(response.body))
    except Exception as e:
        logging.error("Error with sending via sendgrid.")
        return logging.error(e.message)
