"""Gunicorn configuration used for production web server."""

import multiprocessing

bind = "unix:/tmp/compclub.sock"
workers = multiprocessing.cpu_count() * 2 + 1
