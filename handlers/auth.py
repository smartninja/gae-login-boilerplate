import logging
import datetime
import time

from google.appengine.api import app_identity

from handlers.base import BaseHandler
from models.user import User
from utils.check_localhost import is_local
from utils.decorators import login_required
from utils.email_sender import send_email


class RegistrationHandler(BaseHandler):
    def get(self):
        return self.render_template("registration.html")

    def post(self):
        email = self.request.get("registration_email")
        password = self.request.get("registration_password")
        repeat = self.request.get("registration_password_repeat")

        if password == repeat:
            user, message = User.create(email=email, password=password)
            return self.write(message)
        else:
            return self.write("Your password entries do not match.")


class VerifyEmailHandler(BaseHandler):
    def get(self, token):
        params = {}

        if User.verify_email_address(token=token):
            params["message"] = "Email verified! Now you can login."
        else:
            params["message"] = "Email could not be verified..."

        return self.render_template("verify_email.html", params=params)


class LoginHandler(BaseHandler):
    def get(self):
        return self.render_template("login.html")

    def post(self):
        destination = self.request.get("destination")
        email = self.request.get("login_email")
        password = self.request.get("login_password")

        if not email or not password:
            return self.write("Email or password missing.")

        if User.verify_login(email=email, password=password, request=self.request, response=self.response):
            if not destination:
                destination = "/"  # main page

            if is_local():
                time.sleep(2)  # this is needed because datastore lags on localhost

            return self.redirect(destination)  # take user to the destination that s/he wanted to get to
        else:
            return self.write("Login failed.")


class LogoutHandler(BaseHandler):
    @login_required
    def post(self):
        session_token = self.request.cookies.get("ninja_cookie")

        User.remove_session_token(user=self.user, cookie_hash=User.hash_token(session_token), response=self.response)

        return self.redirect_to("main")


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
