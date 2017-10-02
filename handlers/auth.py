import logging
import datetime

from google.appengine.api import app_identity

from handlers.base import BaseHandler
from models.user import User
from utils.email_sender import send_email


class RegistrationHandler(BaseHandler):
    def get(self):
        return self.render_template("registration.html")

    def post(self):
        email = self.request.get("registration_email")
        password = self.request.get("registration_password")
        repeat = self.request.get("registration_password_repeat")

        if email == repeat:
            user, message = User.create(email=email, password=password)
            return self.write(message)


class LoginHandler(BaseHandler):
    def get(self):
        return self.render_template("login.html")


class ResetEnterEmailHandler(BaseHandler):
    def get(self):
        return self.render_template("reset/reset_enter_email.html")

    def post(self):
        email = self.request.get("reset_email")
        user = User.get_by_email(email=email)

        if user:
            token, expired = User.set_token_hash(user=user, reset=True)

            domain = app_identity.get_default_version_hostname()

            params = {"reset_url": "https://{0}/reset-password/new-password?token={1}".format(domain, token)}
            subject = "Reset password"
            template = "reset_password"
            email_sent = send_email(template=template, template_params=params, receiver_email=email, email_subject=subject)

            if email_sent:
                return self.render_template("reset/reset_email_sent.html")
            else:
                self.error(500)
                logging.error("Error with sending reset email for user {}".format(user.get_id))
                return self.write("There was an error processing this request.")
        else:
            return self.render_template("reset/reset_email_not_exist.html")


class ResetEnterPasswordHandler(BaseHandler):
    def get(self):
        token = self.request.get("token")

        if token:
            user = User.query(User.reset_token_hash == User.hash_token(token)).get()

            if user and user.reset_token_expired < datetime.datetime.now():
                return self.render_template("reset/reset_token_expired.html")

            if user:
                params = {"this_user": user}
                return self.render_template("reset/reset_enter_password.html", params=params)

        return self.redirect_to("oops")

    def post(self):
        token = self.request.get("token")
        password = self.request.get("reset_new_password")
        repeat = self.request.get("reset_repeat_password")

        if password != repeat or not password:
            return self.render_template("reset/reset_password_not_match.html")

        if token:
            user = User.query(User.reset_token_hash == User.hash_token(token)).get()

            if user.reset_token_expired < datetime.datetime.now():
                return self.render_template("reset/reset_token_expired.html")

            if user:
                User.set_password_hash(user=user, password=password)  # set new password
                return self.render_template("reset/reset_password_success.html")

        return self.redirect_to("oops")
