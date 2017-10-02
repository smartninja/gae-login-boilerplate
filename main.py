#!/usr/bin/env python
import webapp2

from handlers.auth import RegistrationHandler, LoginHandler
from handlers.base import MainHandler
from handlers.dashboard import DashboardHandler
from workers.send_email_worker import SendEmailWorker

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="main"),
    webapp2.Route('/registration', RegistrationHandler, name="registration"),
    webapp2.Route('/login', LoginHandler, name="login"),
    webapp2.Route('/dashboard', DashboardHandler, name="dashboard"),

    # TASK WORKERS
    webapp2.Route('/tasks/send-email', SendEmailWorker, name="task-send-email-worker"),
], debug=True)
