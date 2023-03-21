from app import app

WEBHOOK_SSL_CERT = "./webhook_cert.pem"  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = "./webhook_pkey.pem"  # Path to the ssl private key

if __name__ == "__main__":
    app.run(ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV))
