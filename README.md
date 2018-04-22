# compclub-web

Dependencies:
- Python 3+
- Django 2.0.4+

Starting the development server:
- Your dev server will need a secret key environment variable. To generate a secret key for development, 
    either run `setSecretKey.ps1` (for Windows users) or `sh setSecretKey.sh` (for Unix users). You only 
    have to do this once per terminal session.
- Run `python manage.py runserver`