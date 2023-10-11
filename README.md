# online-rpg-api

Server application for another [app](https://github.com/bartoszbialoglowicz/rpg-online)

## Installation

We need to create virtual enviroment first
```bash
> cd online-rpg-api
> python -m venv env
```

Let's activate the virtual enviroment
```bash
> env\Scripts\activate
```
Our virtual enviroment is ready.
Use the package manager [pip](https://pip.pypa.io/en/stable/) to install required packages.

```bash
(env) > python -m pip install -r requirements.txt
```
Then we need to make migrations to create structure for our database
```bash
(env) > cd app
(env) > python manage.py makemigrations
(env) > python manage.py migrate
```
Our database is ready so we can start our application
```bash
(env) > python manage.py runserver
```
or if we want our application to be accessible in our local network:
```bash
(env) > python manage.py runserver 0.0.0.0:8000
```
Our server is running now
```bash
Django version 4.2.1, using settings 'app.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```
If you are using as a backend for my another [app](https://github.com/bartoszbialoglowicz/rpg-online), you should also add ip address for frontend-app in settings.py.

online-rpg-api\app\app\settings.py:
```python
ALLOWED_HOSTS = [
    ...
    'your ip' # fe: '192.168.0.10',
    ...
]

...

CORS_ALLOWED_ORIGINS = [
    ...
    'your_address', #fe: 'http://192.168.0.10:3000',
    ...
]

```

Application is ready to use now

