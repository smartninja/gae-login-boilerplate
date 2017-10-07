import hashlib
import hmac
import uuid

import logging

import datetime
from google.appengine.ext import ndb
from google.appengine.api import app_identity

from utils.email_sender import send_email
from utils.secrets import get_pepper


class Token(ndb.Model):
    token_hash = ndb.StringProperty(indexed=True)
    expired = ndb.DateTimeProperty(indexed=True)
    ip = ndb.StringProperty(indexed=True)
    os = ndb.StringProperty(indexed=False)
    created = ndb.DateTimeProperty(auto_now_add=True, indexed=False)


class User(ndb.Model):
    email = ndb.StringProperty(indexed=True)
    verified_email = ndb.BooleanProperty(default=False, indexed=True)
    password_hash = ndb.StringProperty(indexed=False)
    session_token_hashes = ndb.StructuredProperty(Token, repeated=True)
    reset_token_hash = ndb.StringProperty(indexed=True)
    reset_token_expired = ndb.DateTimeProperty(indexed=True)
    verify_email_token_hash = ndb.StringProperty(indexed=True)
    verify_email_token_expired = ndb.DateTimeProperty(indexed=True)
    created = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    updated = ndb.DateTimeProperty(auto_now=True, indexed=False)
    deleted = ndb.BooleanProperty(default=False, indexed=True)

    @property
    def get_id(self):
        return self.key.id()

    @classmethod
    def get_by_email(cls, email):
        return cls.query(cls.email == email.lower()).get()

    @classmethod
    def create(cls, email, password):
        user = cls.query(cls.email == email.lower()).get()

        if not user and email.count("@"):
            user = cls(email=email)
            user.put()

            cls.set_password_hash(user=user, password=password)

            token, expired = cls.set_token_hash(user=user, verify_email=True)  # get a "verify email" token

            domain = app_identity.get_default_version_hostname()
            params = {"verify_url": "https://{0}/verify-email/{1}".format(domain, token)}
            send_email(receiver_email=email, email_subject="Verify your email address",
                       template="verify_email.html", template_params=params)
            message = "Registration successful. Now please check your email and verify your email address."
        else:
            message = "Registration failed. User with this email already exists."

        return user, message

    @classmethod
    def get_current_user(cls, request, response):
        if not request or not response:
            return False

        session_token = request.cookies.get("ninja_cookie")

        if session_token:
            user = cls.query(cls.session_token_hashes.token_hash == cls.hash_token(session_token)).get()

            if user:
                return user
            else:
                response.delete_cookie(key="ninja_cookie")

        return False

    @staticmethod
    def _generate_password_hash(user, password, salt=None):
        # we never save raw password in a database. Instead we create a hash out of it.
        pepper = get_pepper()  # create this function in the utils/secrets.py file

        try:
            if not salt:
                salt = uuid.uuid4().hex

            hash_string = hmac.new(key=str(user.get_id),
                                   msg=str(password) + str(salt) + str(pepper),
                                   digestmod=hashlib.sha256).hexdigest()

            return "%s:%s" % (hash_string, salt)
        except Exception, e:
            logging.error(e.message)
            return False

    @classmethod
    def set_password_hash(cls, user, password):
        """
        Class method to set a new password for a user (use this one!).
        :param user: User object
        :param password: New password string
        :return: This method doesn't return anything.
        """
        user.password_hash = cls._generate_password_hash(user, password)
        user.reset_token_expired = datetime.datetime.now()  # set reset token as expired
        user.put()

    @classmethod
    def verify_email_address(cls, token):
        user = cls.query(cls.verify_email_token_hash == cls.hash_token(token)).get()

        if user and user.verify_email_token_expired > datetime.datetime.now():
            user.verified_email = True
            user.verify_email_token_expired = datetime.datetime.now()
            user.put()

            return True
        else:
            return False

    @classmethod
    def verify_login(cls, email, password, request, response):
        user = cls.query(cls.email == email.lower()).get()

        if not user or not password:
            return False

        if not user.password_hash:
            return False

        hash_string, salt = user.password_hash.split(":")
        if user.password_hash == cls._generate_password_hash(user=user, password=password, salt=salt):
            # set session token hash
            session_token, expired = cls.set_token_hash(user=user, request=request)
            response.set_cookie(key="ninja_cookie", value=session_token, expires=expired)
            return True
        else:
            return False

    @classmethod
    def set_token_hash(cls, user, reset=False, verify_email=False, request=None):
        # there are two types of tokens: reset password tokens and login session tokens
        token = cls._generate_token()
        token_hash = cls.hash_token(token=token)

        if reset:
            # reset token
            user.reset_token_hash = token_hash
            expired = datetime.datetime.now() + datetime.timedelta(days=1)
            user.reset_token_expired = expired
        elif verify_email:
            # token for email verification at the registration
            user.verify_email_token_hash = token_hash
            expired = datetime.datetime.now() + datetime.timedelta(days=10)
            user.verify_email_token_expired = expired
        else:
            # session token
            expired = datetime.datetime.now() + datetime.timedelta(days=14)
            token_object = None

            if request:
                try:
                    user_agent_string = str(request.headers['user-agent']).split("(")[1].split(")")[0]  # add user OS
                    ip_string = str(request.remote_addr)  # add user IP address
                    token_object = Token(token_hash=token_hash, expired=expired, ip=ip_string, os=user_agent_string)
                except Exception as e:
                    logging.error(e.message)
            else:
                token_object = Token(token_hash=token_hash, expired=expired)

            if token_object:
                user.session_token_hashes.append(token_object)

        user.put()

        return token, expired

    @staticmethod
    def _generate_token():
        return uuid.uuid4().hex + uuid.uuid4().hex

    @staticmethod
    def hash_token(token):
        return hashlib.sha512(token).hexdigest()

    @classmethod
    def remove_session_token(cls, user, cookie_hash, response=None):
        for token in user.session_token_hashes:
            if token.token_hash == cookie_hash:
                user.session_token_hashes.remove(token)
                user.put()
                if response:
                    response.delete_cookie(key="ninja_cookie")

    @classmethod
    def reset_password(cls, reset_token, password=None, repeat=None):
        user = cls.query(cls.reset_token_hash == cls.hash_token(token=reset_token)).get()

        if user:
            if user.reset_token_expired > datetime.datetime.now():
                if password and repeat:
                    if password == repeat:
                        cls.set_password_hash(user=user, password=password)
                        return user

        return False
