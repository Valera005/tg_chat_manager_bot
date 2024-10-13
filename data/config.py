import datetime
import ssl

BOT_TOKEN = "YOUR_TOKEN"

DB_USER = "postgres"
DB_PASS = "pass"
DB_NAME = "db_name"
DB_HOST = "127.0.0.1"


time_delta = datetime.timedelta(hours=0)
time_delta_postgres = "'0 hours'::interval"

# to run bot on webhook
# IP = "127.0.0.1"
# WEBHOOK_HOST = f"https://{IP}"
# WEBHOOK_PORT = 8443
# WEBHOOK_PATH = f"/bot/{BOT_TOKEN}"
# WEBHOOK_URL = f"{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}"
#
# #webserver settings
# WEBAPP_HOST = "0.0.0.0"
# WEBAPP_PORT = 8443
#
#
# WEBHOOK_SSL_CERT = "path_to_pem.pem"
# WEBHOOK_SSL_PRIV = "path_to_pkey.pem"
#
#
# ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
# SSL_CERTIFICATE = open(WEBHOOK_SSL_CERT, "rb").read()
# ssl_context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)