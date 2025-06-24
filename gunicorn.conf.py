# Configuración de Gunicorn para Render.com
# Aumenta timeouts y mejora manejo de memoria

# Configuración básica
bind = "0.0.0.0:10000"
workers = 2
worker_class = "sync"
worker_connections = 1000

# Timeouts aumentados para evitar problemas con el scraper
timeout = 300  # 5 minutos
keepalive = 5
graceful_timeout = 300
worker_tmp_dir = "/dev/shm"

# Configuración de memoria
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configuración de seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Configuración de procesos
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# Configuración de SSL (si es necesario)
# keyfile = None
# certfile = None

# Configuración de proxy
forwarded_allow_ips = '*'
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
} 