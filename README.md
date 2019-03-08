# REST API based social network

REST API based social network, with automated bot that demonstrates usage of API
## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements.txt.

In settings.py, adjust PostgreSQL database settings

```bash
## Install requirements
pip install -r requirements.txt```

## Usage


python manage.py makemigrations
python manage.py migrate
python manage.py runserver

## Testing
python manage.py test social

## Automated bot
python manage.py social_bot

```

