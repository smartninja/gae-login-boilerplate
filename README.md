# About

GAE python boilerplate with integrated registration & login system to jumpstart your projects.

## utils/secrets.py

Copy `secrets_template.py` file in the `utils` folder and rename it to `secrets.py`.

## Dependencies

The project allows the use of SendGrid as your emailing provider, so make sure you install Python requirements to the 
libs folder by running the following in the terminal: - `pip install -t libs -r requirements.txt` 
or `pip install -t libs -r requirements.txt --upgrade`

## Cloud SDK and running the project

Make sure you have Cloud SDK installed. You can run the project by typing `sh run.sh` in the terminal (Mac & Linux). On Windows run just `run.sh` command in Git Bash or similar program that can read shell scripts.

## Emailing

SendGrid is preferred over GCloud native emails (they are rate-limited). If you receive over quota error when testing 
how registration works (verify email), then just go to the datastore and manually change email_verified field in User 
to True.

## Localhost issues

Logging in might not work sometimes on localhost due to the datastore lag. The app still works on a server.

## Deployment

- `gcloud init` (always use a new configuration and create a new project - unless you created one on Cloud Console before)
- `gcloud app create --region=europe-west` (this creates a new GAE app within the Google Cloud project)
- `gcloud app deploy app.yaml cron.yaml index.yaml queue.yaml --version main` (this uploads all the necessary yaml files and names the version "main". If there are some yaml files missing, remove them from this command.)
- `gcloud app browse` (this opens up the app URL in your browser)

## Bootstrap

If you want the Bootstrap version, use the `bootstrap` branch.