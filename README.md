# Django Demo
A barebones Django application showcasing [Sevalla's application hosting](https://sevalla.com/application-hosting/).

---
Sevalla is the intuitive platform and the perfect home for your web projects. Deploy applications, databases, and static sites effortlessly.

## Dependency Management
Django is a Python-based web framework, so during the build process Sevalla will automatically install dependencies 
defined in your `requirements.txt` file.

## Environment Variables

Note that the `SECRET_KEY` should not be stored in your repository, but rather set up in an environment 
variable. Set a random string in your newly created app's environment variables tab and make it 
available as both build and runtime variables. Finally, redeploy your application to make the changes effective.

## Web Server Setup

When deploying an application Sevalla will automatically create a web processes, which will fire up `gunicorn`.