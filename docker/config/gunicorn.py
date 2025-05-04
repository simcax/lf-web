# Made from https://github.com/nickjj/build-a-saas-app-with-flask
import multiprocessing
import os

bind = os.getenv("WEB_BIND", "0.0.0.0:8000")
accesslog = "-"
access_log_format = (
    "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s' in %(D)sµs"  # noqa: E501
)

workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2))
threads = int(os.getenv("PYTHON_MAX_THREADS", 1))


reload = os.getenv("WEB_RELOAD", "false").lower() in ("true", "1")

limit_request_line = 0
limit_request_field_size = 0
