# -*- coding: utf-8 -*-
import os
import jinja2
from google.appengine.api import taskqueue

template_dir = os.path.join(os.path.dirname(__file__), '../templates/emails')


def send_email(receiver_email, email_subject, template, sender_email=None, sender_name=None, template_params=None):
    if not sender_email:
        sender_email = "your@authorized.email"  # make sure you authorize this email on Google Cloud Console for this project
        sender_name = "Your Name"

    jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                                   extensions=['jinja2.ext.autoescape'],
                                   autoescape=False)

    html_template = jinja_env.get_template(template)

    if not template_params:
        template_params = {}

    html_message_body = html_template.render(template_params)

    task_params = {
        "sender_email": sender_email,
        "sender_name": sender_name,
        "email_subject": email_subject,
        "content": html_message_body,
        "receiver_email": receiver_email,
    }

    taskqueue.add(
        queue_name="email-queue",
        url="/tasks/send-email",
        params=task_params
    )
