# compclub-web

Dependencies:
- Python 3+
- Django 2.0.4+

Starting the development server:
- Run `python manage.py runserver`

## Setting up your development environment
- Download and install the latest version of Python 3 from [https://python.org] or from your favourite package manager. 
    - You can check that it's installed by running `python --version` in the command line
    - You may get "Python 2.x" instead on Unix systems (e.g. OSX, Linux). If this is the case, try `python3`.
- Download and install `pip` (a Python package manager) from [https://bootstrap.pypa.io/get-pip.py]
    - To install it, run `python get-pip.py`. You may have to do `python3 get-pip.py` instead.
- Install `virtualenv` by running `pip install virtualenv`. You may need to run this in `sudo` mode on Unix systems.
    - We'll be using `virtualenv` to set up a virtual environment to develop in. 
    This [article](https://www.davidfischer.name/2010/04/why-you-should-be-using-pip-and-virtualenv/) 
    and this [article](https://realpython.com/python-virtual-environments-a-primer/#what-is-a-virtual-environment)
    explains why it's good to use virtual environments.
- Download and install `git` from [https://git-scm.com/] or your favourite package manager.
- Navigate to a directory where you want to store your copy of the project using the command line. 
    Then clone the compclub website reposition (e.g. `git clone https://github.com/WeilonYing/compclub-web.git`).
- Then set up your virtual environment by running `virtualenv venv`. On Unix systems, 
    you may need to do `virtualenv venv --python=/usr/bin/python3` to force it to use Python 3.
    - On Windows, activate your virtual environment by running `venv/Scripts/activate`
    - On Unix, activate it by running `venv/bin/activate`
- Almost done! Install Django into your virtual environment by running `pip install django`
- To start a local development server, navigate to `compclub-web/compclub` and run `python manage.py runserver`.
- You should now be able to see a local copy of the website by navigating to `127.0.0.1:5000` in your web browser.

    

