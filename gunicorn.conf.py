# Gunicorn configuration file for FastAPI app
import os
from logging.config import dictConfig
import logging
from logging.handlers import RotatingFileHandler
import multiprocessing

# Application path
wsgi_app = "application:app"

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = 3 #number of workers spawned = 2 x (num. of cores) + 1  
threads = 1 #number of threads per worker
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
timeout = 300
keepalive = 2

# Process naming
proc_name = "hci"

# Logging
errorlog = "/hci/logs/nova.log"
loglevel = "info" 
capture_output = True
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'

# Server mechanics
daemon = True
pidfile = "/hci/logs/nova.pid"
user = "ubuntu" 
group = "ubuntu"  
umask = 0o007
tmp_upload_dir = "/hci/tmp" 

# SSL config
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Server hooks
def on_starting(server):
    pass

def on_reload(server):
    pass

def on_exit(server):
    pass

# Max requests and max requests jitter
max_requests = 1000
max_requests_jitter = 50

# Limit server resources
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190