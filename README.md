# About

GAE python boilerplate with integrated registration&login system to jumpstart your projects.

## utils/secrets.py

Create a secrets.py file in the utils folder.

Add the following functions that encapsulate secret variables, like this:

    def get_sendgrid_api_key():
        return "sendgrid-key-here"
    
    def get_pepper():
        return "pepper-string-here"

## Dependencies

The project allows the use of SendGrid as your emailing provider, so make sure you install Python requirements to the 
libs folder by running the following in the terminal: - `pip install -t libs -r requirements.txt` 
or `pip install -t libs -r requirements.txt --upgrade`

## Cloud SDK and running the project

Make sure you have Cloud SDK installed. You can run the project by typing `sh run.sh` in the terminal.


