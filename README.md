![SLAP UI](/assets/snip.png)

# SLAP - Slim Application Platform

Dear Salesforce, thank you for getting rid of Heroku's free tier. It has inspired me to build my own application hosting platform. 

## Description
SLAP is a web application to control/execute other programs remotely. Most of it's features are self explanatory but here's a list: 

- Add, remove, edit projects
- Configure update & start commands
- Configure environment variables
- Autostart -- run the project on startup
- Restart, stop, start projects
- View logs
- View status
- Password protected
- Automated cloning of projects from git (if provided git url)

## How to use
Clone this repo and setup your machine to run this project on startup. Add a .env file locally with the following variables: 
```
SECRET_KEY=<some random string>
PCR_USERNAME=<username>
PCR_PASSWORD=<password>
PROJECTS_DIR=<the directory in which the projects should be stored>
RESTART_CMD=<a command to open up a new terminal that reruns this project>
TEMPLATES_AUTO_RELOAD=<a flask thing; "yes"/"no">
RUN_CLOUDFLARED=<run cloudflared? "yes"/"no">
CLOUDFLARED_DOMAIN=<if you want to connect this to a cloudflared domain put it here>
```

## The Stack
![Flask](/assets/flask.png)
![Tailwind](/assets/tailwind.png)
![HTMX](/assets/htmx.png)