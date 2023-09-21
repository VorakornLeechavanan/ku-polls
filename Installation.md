# Installation

Clone the GitHub repository

```
git clone https://github.com/VorakornLeechavanan/ku-polls.git
```

Creating a virtual environment

```
python -m venv env
```

Activate a virtual environment

```
. env/bin/activate
```

Download all required libraries from "requirements.txt" file to a user device.

```
pip install -r requirements.txt
```

Migrate a django application
```
python manage.py migrate
```

Run the application tests
```
python manage.py test
```

Run the server

```
python manage.py runserver
```