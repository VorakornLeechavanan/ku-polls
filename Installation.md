# Installation

Clone the GitHub repository

```
git clone https://github.com/VorakornLeechavanan/ku-polls.git
```

Creating a virtual environment

```
python -m venv venv
```

Activate a virtual environment

- For MacOS or Linux
```
source venv/bin/activate
```

- For Windows
```
venv\Scripts\activate
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

Load the data

```
python manage.py loaddata data/users.json
```
```
python manage.py loaddata data/polls.json
```

* load the data from the users.json first and then polls.json to prevent an error


Run the server

```
python manage.py runserver
```
