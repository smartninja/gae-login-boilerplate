#!/usr/bin/env python
import webapp2

from handlers.auth import RegistrationHandler, LoginHandler, ResetEnterEmailHandler, ResetEnterPasswordHandler, \
    VerifyEmailHandler, LogoutHandler
from handlers.base import MainHandler
from handlers.dashboard import DashboardHandler
from workers.send_email_worker import SendEmailWorker

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="main"),
    webapp2.Route('/registration', RegistrationHandler, name="registration"),
    webapp2.Route('/login', LoginHandler, name="login"),
    webapp2.Route('/logout', LogoutHandler, name="logout"),
    webapp2.Route('/dashboard', DashboardHandler, name="dashboard"),

    webapp2.Route('/verify-email/<token:.+>', VerifyEmailHandler, name="verify-email"),

    webapp2.Route('/reset-password/enter-email', ResetEnterEmailHandler, name="reset-enter-email"),
    webapp2.Route('/reset-password/new-password', ResetEnterPasswordHandler, name="reset-enter-password"),

    # TASK WORKERS
    webapp2.Route('/tasks/send-email', SendEmailWorker, name="task-send-email-worker"),
], debug=True)
