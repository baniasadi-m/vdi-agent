# import multiprocessing
from os import environ


bind = environ.get("VDI_GUNICORN_BIND")
# workers = multiprocessing.cpu_count() * 2 + 1
workers = "4"
keepalive = int(environ.get("VDI_GUNICORN_KEEPALIVE"))
timeout = environ.get("VDI_GUNICORN_TIMEOUT")
graceful_timeout = environ.get("VDI_GUNICORN_GRACEFUL_TIMEOUT")
max_requests = environ.get("VDI_GUNICORN_MAXREQUEST")
accesslog = environ.get("VDI_GUNICORN_ACCESSLOG")
errorlog = environ.get("VDI_GUNICORN_ERRORLOG")
loglevel = environ.get("VDI_GUNICORN_LOGLEVEL")
certfile = environ.get("VDI_GUNICORN_SSL_CERT")
keyfile = environ.get("VDI_GUNICORN_SSL_KEY")