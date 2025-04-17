import multiprocessing

# Gunicorn configuration file
bind = "0.0.0.0:10000"  # Render assigns port via PORT env var
workers = multiprocessing.cpu_count() * 2 + 1
timeout = 120  # 2 minutes
worker_class = "gevent"
worker_connections = 1000